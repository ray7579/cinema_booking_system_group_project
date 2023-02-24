from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager

class UserAccountManager(BaseUserManager):
	def create_user(self , email , password = None):
		if not email or len(email) <= 0 :
			raise ValueError("Email field is required !")
		if not password :
			raise ValueError("Password is must !")
		
		user = self.model(
			email = self.normalize_email(email) ,
		)
		user.set_password(password)
		user.save(using = self._db)
		return user
	
	def create_superuser(self , email , password):
		user = self.create_user(
			email = self.normalize_email(email) ,
			password = password
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using = self._db)
		return user
	
class UserAccount(AbstractBaseUser):
	class Types(models.TextChoices):
		STUDENT = "STUDENT" , "student"
		TEACHER = "TEACHER" , "teacher"
		
	type = models.CharField(max_length = 8 , choices = Types.choices ,
							# Default is user is teacher
							default = Types.TEACHER)
	email = models.EmailField(max_length = 200 , unique = True)
	is_active = models.BooleanField(default = True)
	is_admin = models.BooleanField(default = False)
	is_staff = models.BooleanField(default = False)
	is_superuser = models.BooleanField(default = False)
	
	# special permission which define that
	# the new user is teacher or student
	is_student = models.BooleanField(default = False)
	is_teacher = models.BooleanField(default = False)
	
	USERNAME_FIELD = "email"
	
	# defining the manager for the UserAccount model
	objects = UserAccountManager()
	
	def __str__(self):
		return str(self.email)
	
	def has_perm(self , perm, obj = None):
		return self.is_admin
	
	def has_module_perms(self , app_label):
		return True
	
	def save(self , *args , **kwargs):
		if not self.type or self.type == None :
			self.type = UserAccount.Types.TEACHER
		return super().save(*args , **kwargs)