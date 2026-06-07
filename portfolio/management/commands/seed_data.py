"""Seed the database with sample portfolio data."""

from django.core.management.base import BaseCommand
from portfolio.models import (
    Profile, SkillCategory, Skill, ProjectCategory, Project,
    Education, Experience, Achievement, Publication, Testimonial
)
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Seed the database with sample portfolio data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding portfolio data...')

        # Site Settings
        site, _ = SiteSettings.objects.get_or_create(pk=1, defaults={
            'site_title': 'Rakib - 3D Portfolio',
            'site_description': 'A next-generation 3D interactive portfolio showcasing physics, development, and research.',
            'hero_title': "Hello, I'm",
            'hero_name': 'Rakib',
            'hero_roles': ['Physicist', 'Developer', 'Researcher', 'Problem Solver', 'Innovator'],
            'hero_subtitle': 'Building the future at the intersection of physics and technology.',
            'email': 'hello@rakib.dev',
            'github_url': 'https://github.com/rakib',
            'linkedin_url': 'https://linkedin.com/in/rakib',
        })
        self.stdout.write(self.style.SUCCESS('[OK] Site settings created'))

        # Profile
        profile, _ = Profile.objects.get_or_create(full_name='Rakib', defaults={
            'title': 'Physicist & Full-Stack Developer',
            'bio': 'I am a multidisciplinary professional at the intersection of physics, technology, and innovation. With a deep foundation in scientific research and modern software development, I bring a unique perspective to every project I undertake. My journey has taken me from theoretical physics to full-stack development, from academic research to building production-grade applications.',
            'location': 'World',
            'email': 'hello@rakib.dev',
            'interests': ['Physics', 'AI/ML', 'Web Development', 'Data Science', 'Mathematics', 'Open Source'],
            'research_areas': ['Quantum Computing', 'Machine Learning', 'Computational Physics', 'Data Visualization'],
            'personal_story': 'Started my journey in physics, discovered programming, and never looked back. I believe in the power of interdisciplinary thinking.',
            'fun_facts': ['Can solve a Rubik\'s cube in under 60 seconds', 'Has contributed to 5+ open source projects', 'Fluent in 3 programming languages and 2 human languages'],
        })
        self.stdout.write(self.style.SUCCESS('[OK] Profile created'))

        # Skills
        dev_cat, _ = SkillCategory.objects.get_or_create(name='Development', defaults={
            'icon': 'code', 'color': '#3B82F6', 'order': 1
        })
        physics_cat, _ = SkillCategory.objects.get_or_create(name='Physics & Math', defaults={
            'icon': 'atom', 'color': '#7C3AED', 'order': 2
        })
        data_cat, _ = SkillCategory.objects.get_or_create(name='Data Science & AI', defaults={
            'icon': 'brain', 'color': '#00FFFF', 'order': 3
        })
        tools_cat, _ = SkillCategory.objects.get_or_create(name='Tools & Platforms', defaults={
            'icon': 'wrench', 'color': '#4F46E5', 'order': 4
        })

        skills_data = [
            ('Python', dev_cat, 5), ('Django', dev_cat, 5), ('JavaScript', dev_cat, 4),
            ('React', dev_cat, 4), ('Three.js', dev_cat, 4), ('TypeScript', dev_cat, 3),
            ('PostgreSQL', dev_cat, 4), ('Docker', dev_cat, 3),
            ('Theoretical Physics', physics_cat, 5), ('Quantum Mechanics', physics_cat, 4),
            ('Mathematics', physics_cat, 5), ('Computational Physics', physics_cat, 4),
            ('Machine Learning', data_cat, 5), ('Data Science', data_cat, 4),
            ('Deep Learning', data_cat, 4), ('SQL', data_cat, 4),
            ('Git', tools_cat, 5), ('Linux', tools_cat, 4), ('AWS', tools_cat, 3),
            ('Redis', tools_cat, 3), ('Celery', tools_cat, 3),
        ]
        for name, cat, prof in skills_data:
            Skill.objects.get_or_create(name=name, defaults={
                'category': cat, 'proficiency': prof, 'is_featured': prof >= 4
            })
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(skills_data)} skills created'))

        # Project Categories
        cats = {}
        for name, slug, color in [
            ('Web Development', 'web-dev', '#3B82F6'),
            ('AI & Machine Learning', 'ai-ml', '#7C3AED'),
            ('Physics', 'physics', '#00FFFF'),
            ('Data Science', 'data-science', '#4F46E5'),
            ('Research', 'research', '#10B981'),
        ]:
            cat, _ = ProjectCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'color': color})
            cats[slug] = cat
        self.stdout.write(self.style.SUCCESS('[OK] Project categories created'))

        # Projects
        projects_data = [
            ('Quantum Visualizer', 'ai-ml', 'Interactive 3D quantum mechanics visualization tool using Three.js and WebGL shaders.', True, ['Three.js', 'WebGL', 'Python', 'Django']),
            ('Neural Network Playground', 'ai-ml', 'Browser-based neural network training and visualization platform.', True, ['React', 'TensorFlow.js', 'Django', 'PostgreSQL']),
            ('Physics Simulation Engine', 'physics', 'Real-time physics simulation engine with particle systems and collision detection.', True, ['Python', 'C++', 'OpenGL', 'NumPy']),
            ('Data Observatory', 'data-science', 'Interactive data exploration and visualization dashboard for scientific datasets.', False, ['React', 'D3.js', 'Django', 'PostgreSQL']),
            ('Portfolio 3.0', 'web-dev', 'This very portfolio - a next-generation 3D interactive experience.', True, ['Django', 'Three.js', 'GSAP', 'Tailwind CSS']),
            ('Research Hub', 'research', 'Collaborative research platform for managing papers, citations, and collaborations.', False, ['Django', 'React', 'Elasticsearch']),
        ]
        for title, cat_slug, desc, featured, techs in projects_data:
            Project.objects.get_or_create(title=title, defaults={
                'description': desc,
                'category': cats.get(cat_slug),
                'featured': featured,
                'technologies': techs,
                'status': 'completed',
                'github_url': f'https://github.com/rakib/{title.lower().replace(" ", "-")}',
            })
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(projects_data)} projects created'))

        # Education
        Education.objects.get_or_create(
            institution='University of Technology',
            degree='Ph.D.',
            field_of_study='Theoretical Physics',
            defaults={
                'description': 'Focused on quantum field theory and computational methods.',
                'gpa': '3.95/4.0',
                'start_date': '2018-09-01',
                'end_date': '2023-06-01',
            }
        )
        Education.objects.get_or_create(
            institution='University of Technology',
            degree='B.Sc.',
            field_of_study='Physics & Computer Science',
            defaults={
                'description': 'Double major with honors.',
                'gpa': '3.85/4.0',
                'start_date': '2014-09-01',
                'end_date': '2018-06-01',
            }
        )
        self.stdout.write(self.style.SUCCESS('[OK] Education records created'))

        # Experience
        Experience.objects.get_or_create(
            company='TechCorp',
            position='Senior Full-Stack Developer',
            defaults={
                'description': 'Leading the development of next-generation web applications using Django and React.',
                'achievements': ['Led migration to microservices architecture', 'Reduced page load time by 60%', 'Mentored 5 junior developers', 'Implemented CI/CD pipeline'],
                'location': 'Remote',
                'start_date': '2023-07-01',
                'is_current': True,
            }
        )
        Experience.objects.get_or_create(
            company='Research Lab',
            position='Research Scientist',
            defaults={
                'description': 'Conducted cutting-edge research in quantum computing and machine learning applications in physics.',
                'achievements': ['Published 8 peer-reviewed papers', 'Developed novel quantum algorithm', 'Secured $50K research grant', 'Collaborated with international team'],
                'location': 'Boston, MA',
                'start_date': '2020-01-01',
                'end_date': '2023-06-01',
            }
        )
        self.stdout.write(self.style.SUCCESS('[OK] Experience records created'))

        # Achievements
        achievements_data = [
            ('Best Paper Award', 'award', 'International Conference on Quantum Computing', '2023-03-15'),
            ('Dean\'s Scholarship', 'scholarship', 'University of Technology', '2020-09-01'),
            ('AWS Solutions Architect', 'certification', 'Amazon Web Services', '2023-08-01'),
            ('Hackathon Winner', 'competition', 'TechCrunch Disrupt', '2022-10-15'),
            ('Open Source Contributor Award', 'award', 'GitHub', '2023-01-20'),
        ]
        for title, a_type, org, date in achievements_data:
            Achievement.objects.get_or_create(title=title, defaults={
                'achievement_type': a_type,
                'organization': org,
                'date': date,
                'description': f'Recognized for excellence in {title.lower()}.',
                'featured': True,
            })
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(achievements_data)} achievements created'))

        # Publications
        pubs_data = [
            ('Quantum-Enhanced Machine Learning for Particle Physics', 'Physical Review Letters',
             'We present a novel approach to particle physics analysis using quantum-enhanced machine learning algorithms...',
             '2023-05-15', 45, 'journal'),
            ('Deep Learning Approaches to Quantum State Reconstruction', 'Nature Quantum Information',
             'This paper explores the application of deep neural networks for efficient quantum state reconstruction...',
             '2022-11-20', 32, 'journal'),
            ('Real-Time Physics Simulation Using GPU Computing', 'Conference on Computational Physics',
             'We demonstrate a GPU-accelerated physics simulation engine capable of real-time particle interactions...',
             '2022-07-10', 18, 'conference'),
        ]
        for title, journal, abstract, date, citations, p_type in pubs_data:
            Publication.objects.get_or_create(title=title, defaults={
                'authors': 'Rakib et al.',
                'journal': journal,
                'abstract': abstract,
                'date': date,
                'citations': citations,
                'publication_type': p_type,
            })
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(pubs_data)} publications created'))

        # Testimonials
        testimonials_data = [
            ('Dr. Sarah Chen', 'Professor of Physics', 'MIT',
             'Rakib is one of the most talented researchers I\'ve had the pleasure of working with. His ability to bridge physics and computer science is truly remarkable.'),
            ('James Wilson', 'CTO', 'TechCorp',
             'Working with Rakib was a game-changer for our team. His technical skills are matched only by his creativity and problem-solving ability.'),
            ('Maria Garcia', 'Senior Data Scientist', 'DeepMind',
             'Rakib\'s contributions to our quantum ML project were invaluable. He brought both deep theoretical knowledge and practical engineering skills.'),
            ('Alex Thompson', 'Research Director', 'Quantum Lab',
             'A rare talent who can move seamlessly between theoretical physics and production software development. Highly recommended.'),
        ]
        for name, title, company, content in testimonials_data:
            Testimonial.objects.get_or_create(name=name, defaults={
                'title': title,
                'company': company,
                'content': content,
                'rating': 5,
                'featured': True,
            })
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(testimonials_data)} testimonials created'))

        self.stdout.write(self.style.SUCCESS('\n>>> Database seeded successfully!'))
        self.stdout.write('Run: python manage.py runserver')
        self.stdout.write('Visit: http://127.0.0.1:8000')
        self.stdout.write('Admin: http://127.0.0.1:8000/admin')
