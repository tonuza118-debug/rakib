"""Test Cloudinary upload directly via Django ORM."""
import struct, zlib, io, time
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management.base import BaseCommand
from portfolio.models import Project
import cloudinary
from django.conf import settings
import urllib.request


class Command(BaseCommand):
    help = "Test Cloudinary upload and verify URL resolves"

    def handle(self, *args, **options):
        # Create test PNG
        sig = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 10, 10, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        raw = b'\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00' * 25
        compressed = zlib.compress(raw)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        png_data = sig + ihdr + idat + iend

        buf = io.BytesIO(png_data)
        png = InMemoryUploadedFile(buf, 'image', 'test_cmd.png', 'image/png', len(png_data), None)

        self.stdout.write("=" * 60)
        self.stdout.write("CLOUDINARY UPLOAD TEST")
        self.stdout.write("=" * 60)

        # Test 1: Direct cloudinary upload
        self.stdout.write("\n--- Test 1: Direct cloudinary.uploader.upload ---")
        result = cloudinary.uploader.upload(
            png_data,
            public_id='test_direct_cmd',
            use_filename=False,
            unique_filename=False,
            overwrite=True,
        )
        self.stdout.write(f"  Sent public_id: test_direct_cmd")
        self.stdout.write(f"  Response public_id: {result['public_id']}")
        self.stdout.write(f"  Secure URL: {result['secure_url']}")
        if result['public_id'] == 'test_direct_cmd':
            self.stdout.write(self.style.SUCCESS("  ✓ public_id matches!"))
        else:
            self.stdout.write(self.style.ERROR(f"  ✗ MISMATCH! Expected 'test_direct_cmd', got '{result['public_id']}'"))

        # Test 2: Via our custom storage
        self.stdout.write("\n--- Test 2: Via CustomMediaCloudinaryStorage ---")
        from core.storage.custom_cloudinary import CustomMediaCloudinaryStorage
        storage = CustomMediaCloudinaryStorage()

        # Check what _upload does
        import inspect
        src = inspect.getsource(storage._upload)
        has_uf = 'use_filename' in src
        has_uniq = 'unique_filename' in src
        self.stdout.write(f"  _upload has use_filename: {has_uf}")
        self.stdout.write(f"  _upload has unique_filename: {has_uniq}")

        buf2 = io.BytesIO(png_data)
        png2 = InMemoryUploadedFile(buf2, 'image', 'projects/test_cmd_storage.png', 'image/png', len(png_data), None)
        saved = storage.save('projects/test_cmd_storage.png', png2)
        self.stdout.write(f"  Storage saved name: {saved}")
        url = storage.url(saved)
        self.stdout.write(f"  Storage URL: {url}")
        if saved == 'projects_test_cmd_storage':
            self.stdout.write(self.style.SUCCESS("  ✓ Saved name is correct (underscored, no ext)!"))
        else:
            self.stdout.write(self.style.ERROR(f"  ✗ Expected 'projects_test_cmd_storage', got '{saved}'"))

        # Test 3: Via Django ORM
        self.stdout.write("\n--- Test 3: Via Django ORM (Project.objects.create) ---")
        Project.objects.filter(slug__startswith='test-cmd-').delete()
        ts = int(time.time())
        project = Project.objects.create(
            title=f'Test CMD {ts}',
            slug=f'test-cmd-{ts}',
            description='Test',
            short_description='Test',
            status='completed',
            featured=False,
            order=9999,
            image=png,
        )
        project.refresh_from_db()
        stored = str(project.image.name) if project.image else 'None'
        img_url = project.image.url if project.image else 'None'
        self.stdout.write(f"  Stored name: {stored}")
        self.stdout.write(f"  Image URL: {img_url}")

        if '/' not in stored and '.' not in stored:
            self.stdout.write(self.style.SUCCESS("  ✓ Stored name has no slashes or extensions!"))
        else:
            self.stdout.write(self.style.ERROR(f"  ✗ Stored name has slashes/extensions: {stored}"))

        # Test 4: Verify URL resolves
        self.stdout.write("\n--- Test 4: URL Resolution ---")
        for test_url in [result['secure_url'], img_url]:
            if test_url and test_url != 'None':
                try:
                    req = urllib.request.Request(test_url, method='HEAD')
                    resp = urllib.request.urlopen(req, timeout=10)
                    self.stdout.write(f"  {test_url} -> HTTP {resp.status} ✓")
                except Exception as e:
                    self.stdout.write(f"  {test_url} -> ERROR: {e}")

        # Cleanup
        project.delete()
        self.stdout.write("\n" + "=" * 60)
