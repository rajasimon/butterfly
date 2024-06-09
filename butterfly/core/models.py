from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyProfileManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Profile(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyProfileManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Friend(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="friends"
    )

    class StatusChoice(models.TextChoices):
        ACCEPT = "ACCEPT"
        SEND = "SEND"
        REJECT = "REJECT"

    status = models.CharField(
        max_length=100, choices=StatusChoice.choices, default=StatusChoice.SEND
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str(self):
        return f"{self.owner} - friend {self.profile}"

    class Meta:
        unique_together = ("owner", "profile")
