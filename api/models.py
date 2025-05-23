from django.db import models

class CurrencyAmount(models.Model):
    currency_code = models.CharField(max_length=10)
    amount = models.CharField(max_length=50)

class Locale(models.Model):
    country = models.CharField(max_length=10)
    language = models.CharField(max_length=10)

class RunSchedule(models.Model):
    start = models.BigIntegerField()
    end = models.BigIntegerField()

class AuditStamp(models.Model):
    actor = models.CharField(max_length=100)
    time = models.BigIntegerField()

class ChangeAudit(models.Model):
    created = models.OneToOneField(AuditStamp, related_name='created_audit', on_delete=models.CASCADE)
    last_modified = models.OneToOneField(AuditStamp, related_name='modified_audit', on_delete=models.CASCADE)

class Version(models.Model):
    version_tag = models.CharField(max_length=20)

class OffsitePreferences(models.Model):
    iab_categories_exclude = models.JSONField(default=list)
    publisher_include = models.JSONField(default=list)
    publisher_exclude = models.JSONField(default=list)

class TargetingCriteria(models.Model):
    include = models.JSONField()
    exclude = models.JSONField()

class Campaign(models.Model):
    campaign_id = models.BigIntegerField(unique=True)
    name = models.TextField()
    account = models.CharField(max_length=100)
    campaign_group = models.CharField(max_length=100)
    associated_entity = models.CharField(max_length=100)
    objective_type = models.CharField(max_length=50)
    cost_type = models.CharField(max_length=10)
    pacing_strategy = models.CharField(max_length=50)
    optimization_target_type = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    format = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    total_budget = models.OneToOneField(CurrencyAmount, on_delete=models.CASCADE, related_name='campaign_budget')
    unit_cost = models.OneToOneField(CurrencyAmount, on_delete=models.CASCADE, related_name='campaign_cost')
    run_schedule = models.OneToOneField(RunSchedule, on_delete=models.CASCADE)
    locale = models.OneToOneField(Locale, on_delete=models.CASCADE)
    change_audit_stamps = models.OneToOneField(ChangeAudit, on_delete=models.CASCADE)
    version = models.OneToOneField(Version, on_delete=models.CASCADE)
    offsite_preferences = models.OneToOneField(OffsitePreferences, on_delete=models.CASCADE)
    targeting_criteria = models.OneToOneField(TargetingCriteria, on_delete=models.CASCADE)
    audience_expansion_enabled = models.BooleanField()
    story_delivery_enabled = models.BooleanField()
    offsite_delivery_enabled = models.BooleanField()
    connected_television_only = models.BooleanField()
    test = models.BooleanField()
    serving_statuses = models.JSONField(default=list)
    creative_selection = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CampaignChangeLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="change_logs")
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField()
    changes = models.JSONField()

    def __str__(self):
        return f"ChangeLog for Campaign {self.campaign.id} at {self.changed_at}"
