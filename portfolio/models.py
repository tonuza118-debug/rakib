"""Portfolio data models - all content managed through Django Admin."""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Profile(models.Model):
    """Personal profile information."""
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, help_text="e.g. Physicist & Developer")
    bio = models.TextField()
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True, max_length=500)
    resume = models.FileField(upload_to='profile/', blank=True, null=True, max_length=500)
    location = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    interests = models.JSONField(default=list, blank=True)
    research_areas = models.JSONField(default=list, blank=True)
    personal_story = models.TextField(blank=True)
    fun_facts = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.full_name


class SkillCategory(models.Model):
    """Categories for skills (e.g. Development, Physics, Design)."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, help_text="Lucide icon name")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Individual skills with proficiency levels."""
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'), (2, 'Elementary'), (3, 'Intermediate'),
        (4, 'Advanced'), (5, 'Expert'),
    ]
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=3)
    icon = models.CharField(max_length=100, blank=True, help_text="Lucide/icon class name")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', '-proficiency', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"

    @property
    def proficiency_percent(self):
        return self.proficiency * 20


class ProjectCategory(models.Model):
    """Project categories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=7, default="#7C3AED")

    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """Portfolio projects."""
    STATUS_CHOICES = [
        ('completed', 'Completed'), ('in_progress', 'In Progress'),
        ('planned', 'Planned'), ('archived', 'Archived'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, related_name='projects')
    image = models.ImageField(upload_to='projects/', blank=True, null=True, max_length=500)
    video_url = models.URLField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    technologies = models.JSONField(default=list, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', 'order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.short_description:
            self.short_description = self.description[:300]
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    """Multiple images/screenshots for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/', max_length=500)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class Education(models.Model):
    """Educational background."""
    institution = models.CharField(max_length=300)
    degree = models.CharField(max_length=300)
    field_of_study = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    gpa = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='education/', blank=True, null=True, max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Education"
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    """Work experience."""
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField()
    achievements = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=200, blank=True)
    company_url = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='experience/', blank=True, null=True, max_length=500)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Experience"
        verbose_name_plural = "Experience"

    def __str__(self):
        return f"{self.position} at {self.company}"


class Achievement(models.Model):
    """Awards, honors, certifications."""
    TYPE_CHOICES = [
        ('award', 'Award'), ('scholarship', 'Scholarship'),
        ('certification', 'Certification'), ('competition', 'Competition'),
        ('publication', 'Publication'), ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='award')
    organization = models.CharField(max_length=200, blank=True)
    date = models.DateField(blank=True, null=True)
    certificate = models.FileField(upload_to='achievements/', blank=True, null=True, max_length=500)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True, max_length=500)
    url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date', 'order']

    def __str__(self):
        return self.title


class Publication(models.Model):
    """Research papers, articles, reports."""
    TYPE_CHOICES = [
        ('journal', 'Journal Paper'), ('conference', 'Conference Paper'),
        ('preprint', 'Preprint'), ('book', 'Book'),
        ('chapter', 'Book Chapter'), ('report', 'Report'),
        ('presentation', 'Presentation'), ('other', 'Other'),
    ]
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    abstract = models.TextField(blank=True)
    publication_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='journal')
    journal = models.CharField(max_length=300, blank=True)
    doi = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    pdf = models.FileField(upload_to='publications/', blank=True, null=True, max_length=500)
    date = models.DateField(blank=True, null=True)
    citations = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Testimonials from colleagues, clients, mentors."""
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True, max_length=500)
    content = models.TextField()
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-featured', 'order']

    def __str__(self):
        return f"{self.name} - {self.title}"


class BlogPost(models.Model):
    """Blog articles."""
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived'),
    ]
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, max_length=500)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:500]
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """Messages from the contact form."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject or '(No subject)'}"


