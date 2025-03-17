import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
import rest_framework


class Command(BaseCommand):
    help = "Copy Django REST Framework static files to the static directory"

    def handle(self, *args, **options):
        # Get the path to the DRF static files
        drf_static_dir = os.path.join(
            os.path.dirname(rest_framework.__file__), "static", "rest_framework"
        )

        # Get the path to the project's static directory
        target_dir = os.path.join(settings.BASE_DIR, "static", "rest_framework")

        # Create the target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)

        # Copy the DRF static files
        self.stdout.write(
            f"Copying DRF static files from {drf_static_dir} to {target_dir}"
        )

        # Walk through the DRF static directory and copy all files
        for root, dirs, files in os.walk(drf_static_dir):
            # Get the relative path from the DRF static directory
            rel_path = os.path.relpath(root, drf_static_dir)

            # Create the corresponding directory in the target directory
            if rel_path != ".":
                os.makedirs(os.path.join(target_dir, rel_path), exist_ok=True)

            # Copy all files in the current directory
            for file in files:
                src_file = os.path.join(root, file)
                if rel_path == ".":
                    dst_file = os.path.join(target_dir, file)
                else:
                    dst_file = os.path.join(target_dir, rel_path, file)
                shutil.copy2(src_file, dst_file)
                self.stdout.write(f"  Copied {src_file} to {dst_file}")

        self.stdout.write(self.style.SUCCESS("Successfully copied DRF static files"))
