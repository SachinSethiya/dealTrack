from django.db import models
from django.contrib.auth.hashers import make_password


class AdminSettings(models.Model):
    """
    Platform-wide settings for the DealTrack application.
    Used by super admin to control platform behavior.
    """
    allow_new_showroom_registration = models.BooleanField(
        default=True,
        help_text="Allow new users to register as showrooms"
    )
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Put the platform in maintenance mode"
    )
    platform_announcement = models.TextField(
        blank=True,
        null=True,
        help_text="Announcement message to display to all users"
    )
    max_showrooms_per_user = models.IntegerField(
        default=1,
        help_text="Maximum number of showrooms a user can create"
    )
    email_notifications_enabled = models.BooleanField(
        default=True,
        help_text="Enable email notifications"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Admin Settings"
        verbose_name_plural = "Admin Settings"
        db_table = "admin_settings"
    
    def __str__(self):
        return f"Admin Settings (Updated: {self.updated_at.strftime('%Y-%m-%d')})"
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance with fallback handling"""
        try:
            settings, created = cls.objects.get_or_create(pk=1)
            return settings
        except Exception as e:
            # Handle cases where table doesn't exist or other database issues
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error accessing AdminSettings table: {e}")
            
            # Return a default settings instance without saving to database
            return cls(
                allow_new_showroom_registration=True,
                maintenance_mode=False,
                platform_announcement="",
                max_showrooms_per_user=1,
                email_notifications_enabled=True
            )


