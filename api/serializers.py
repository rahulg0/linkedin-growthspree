from rest_framework import serializers
from .models import *

class CurrencyAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyAmount
        fields = ['currency_code', 'amount']

class LocaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locale
        fields = ['country', 'language']

class RunScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunSchedule
        fields = ['start', 'end']

class AuditStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditStamp
        fields = ['actor', 'time']

class ChangeAuditSerializer(serializers.ModelSerializer):
    created = AuditStampSerializer()
    last_modified = AuditStampSerializer()

    class Meta:
        model = ChangeAudit
        fields = ['created', 'last_modified']

    def create(self, validated_data):
        created_data = validated_data.pop('created')
        last_modified_data = validated_data.pop('last_modified')
        created = AuditStamp.objects.create(**created_data)
        last_modified = AuditStamp.objects.create(**last_modified_data)
        return ChangeAudit.objects.create(created=created, last_modified=last_modified)

class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['version_tag']

class OffsitePreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffsitePreferences
        fields = ['iab_categories_exclude', 'publisher_include', 'publisher_exclude']

class TargetingCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingCriteria
        fields = ['include', 'exclude']

class CampaignSerializer(serializers.ModelSerializer):
    total_budget = CurrencyAmountSerializer()
    unit_cost = CurrencyAmountSerializer()
    locale = LocaleSerializer()
    run_schedule = RunScheduleSerializer()
    change_audit_stamps = ChangeAuditSerializer()
    version = VersionSerializer()
    offsite_preferences = OffsitePreferencesSerializer()
    targeting_criteria = TargetingCriteriaSerializer()

    class Meta:
        model = Campaign
        fields = '__all__'

    def create(self, validated_data):
        total_budget_data = validated_data.pop('total_budget')
        unit_cost_data = validated_data.pop('unit_cost')
        locale_data = validated_data.pop('locale')
        run_schedule_data = validated_data.pop('run_schedule')
        audit_data = validated_data.pop('change_audit_stamps')
        version_data = validated_data.pop('version')
        offsite_prefs_data = validated_data.pop('offsite_preferences')
        targeting_criteria_data = validated_data.pop('targeting_criteria')

        total_budget = CurrencyAmount.objects.create(**total_budget_data)
        unit_cost = CurrencyAmount.objects.create(**unit_cost_data)
        locale = Locale.objects.create(**locale_data)
        run_schedule = RunSchedule.objects.create(**run_schedule_data)
        audit = ChangeAuditSerializer().create(audit_data)
        version = Version.objects.create(**version_data)
        offsite_prefs = OffsitePreferences.objects.create(**offsite_prefs_data)
        targeting_criteria = TargetingCriteria.objects.create(**targeting_criteria_data)

        campaign = Campaign.objects.create(
            total_budget=total_budget,
            unit_cost=unit_cost,
            locale=locale,
            run_schedule=run_schedule,
            change_audit_stamps=audit,
            version=version,
            offsite_preferences=offsite_prefs,
            targeting_criteria=targeting_criteria,
            **validated_data
        )
        return campaign
