# Generated by Django 3.1.1 on 2020-10-23 12:10

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.IntegerField(blank=True, null=True, verbose_name='手机号')),
                ('avatar', models.FileField(default='avatar/default.png', upload_to='avatar/')),
                ('create_time', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': '用户信息',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='文章标题')),
                ('desc', models.CharField(max_length=255, verbose_name='文章简介')),
                ('content', models.TextField(verbose_name='文章内容')),
                ('create_time', models.DateField(auto_now_add=True)),
                ('up_num', models.IntegerField(default=0, verbose_name='点赞数')),
                ('down_num', models.IntegerField(default=0, verbose_name='点踩数')),
                ('comment_num', models.BigIntegerField(default=0, verbose_name='评论数')),
            ],
            options={
                'verbose_name_plural': '文章',
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=32, verbose_name='站点名称')),
                ('site_title', models.CharField(max_length=32, verbose_name='站点标题')),
                ('site_theme', models.CharField(max_length=64, verbose_name='站点样式')),
            ],
            options={
                'verbose_name_plural': '个人站点',
            },
        ),
        migrations.CreateModel(
            name='UpAndDown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_up', models.BooleanField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '调整顺序',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='标签')),
                ('blog', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.blog', verbose_name='站点名称')),
            ],
            options={
                'verbose_name_plural': '标签',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='评论内容')),
                ('comment_time', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.article')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '评论',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='文章分类')),
                ('blog', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.blog')),
            ],
            options={
                'verbose_name_plural': '分类',
            },
        ),
        migrations.CreateModel(
            name='Article_Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.article')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.tag')),
            ],
            options={
                'verbose_name_plural': '文章标签',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='blog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.blog', verbose_name='个人站点'),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.category', verbose_name='分类'),
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(through='app01.Article_Tag', to='app01.Tag'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='blog',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.blog'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
