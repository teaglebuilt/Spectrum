# Generated by Django 2.1 on 2018-09-18 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsLetterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=1000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='post_image')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.UserMembership')),
                ('likes', models.ManyToManyField(blank=True, related_name='post_likes', to='memberships.UserMembership')),
            ],
            options={
                'db_table': 'Post',
            },
        ),
    ]
