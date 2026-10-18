from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document

        fields = [
            'id',
            'candidate',
            'verification',
            'document_type',
            'document_name',
            'file',
            'status',
            'uploaded_by',
            'uploaded_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'uploaded_by',
            'uploaded_at',
            'updated_at',
        ]

    def validate_file(self, file):
        allowed_extensions = [
            '.pdf',
            '.jpg',
            '.jpeg',
            '.png',
        ]
        file_name = file.name.lower()
        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise serializers.ValidationError(
                'Only PDF, JPG, JPEG and PNG files are allowed.'
            )
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError(
                'File size must not exceed 5 MB.'
            )
        return file


class DocumentVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = [
            'status',
        ]

    def validate_status(self, value):
        allowed_statuses = [
            'VERIFIED',
            'REJECTED',
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                'Status must be VERIFIED or REJECTED.'
            )

        return value