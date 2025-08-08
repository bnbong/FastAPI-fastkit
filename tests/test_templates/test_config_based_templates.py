# # --------------------------------------------------------------------------
# # Configuration-based template testing
# #
# # @author bnbong bbbong9@gmail.com
# # --------------------------------------------------------------------------
# import os
# from pathlib import Path
# from typing import Any, Dict, Generator, List

# import pytest
# import yaml
# from click.testing import CliRunner

# from fastapi_fastkit.cli import fastkit_cli
# from fastapi_fastkit.utils.main import is_fastkit_project


# class ConfigBasedTemplateTest:
#     """Configuration-based template testing using YAML config"""

#     runner: CliRunner = CliRunner()

#     @classmethod
#     def load_template_configs(cls) -> Dict[str, Any]:
#         """Load template configurations from YAML file"""
#         config_path = Path(__file__).parent / "template_configs.yaml"

#         try:
#             with open(config_path, "r", encoding="utf-8") as f:
#                 config = yaml.safe_load(f)
#             return config
#         except FileNotFoundError:
#             pytest.skip(f"Template config file not found: {config_path}")
#         except yaml.YAMLError as e:
#             pytest.fail(f"Failed to parse template config: {e}")

#     @classmethod
#     def get_template_names(cls) -> List[str]:
#         """Get all template names from configuration"""
#         config = cls.load_template_configs()
#         return list(config.get("templates", {}).keys())

#     @pytest.fixture
#     def temp_dir(self, tmpdir: Any) -> Generator[str, None, None]:
#         """Temporary directory fixture"""
#         original_cwd = os.getcwd()
#         os.chdir(str(tmpdir))
#         yield str(tmpdir)
#         os.chdir(original_cwd)

#     @pytest.fixture
#     def template_config(self) -> Dict[str, Any]:
#         """Template configuration fixture"""
#         return self.load_template_configs()

#     @pytest.mark.parametrize("template_name", get_template_names.__func__())
#     def test_template_creation_from_config(
#         self, template_name: str, temp_dir: str, template_config: Dict[str, Any]
#     ) -> None:
#         """Test template creation using configuration"""
#         # Given
#         template_info = template_config["templates"][template_name]
#         global_settings = template_config.get("global_settings", {})

#         project_name = f"config-test-{template_name}"
#         author = global_settings.get("default_author", "test-author")
#         author_email = global_settings.get("default_email", "test@example.com")
#         description = template_info.get(
#             "description", f"Test project for {template_name}"
#         )
#         package_manager = template_info.get(
#             "package_manager", global_settings.get("default_package_manager", "uv")
#         )

#         # When
#         result = self.runner.invoke(
#             fastkit_cli,
#             ["startdemo", template_name],
#             input="\n".join(
#                 [project_name, author, author_email, description, package_manager, "Y"]
#             ),
#         )

#         # Then
#         project_path = Path(temp_dir) / project_name

#         # Basic assertions
#         assert (
#             project_path.exists()
#         ), f"Project directory was not created for {template_name}"
#         assert (
#             result.exit_code == 0
#         ), f"CLI command failed for {template_name}: {result.output}"
#         assert (
#             "Success" in result.output
#         ), f"Success message not found for {template_name}"

#         # Template identification
#         assert is_fastkit_project(
#             str(project_path)
#         ), f"Not identified as fastkit project: {template_name}"

#         # Check expected files from config
#         expected_files = template_info.get("expected_files", [])
#         for expected_file in expected_files:
#             file_path = project_path / expected_file
#             assert (
#                 file_path.exists()
#             ), f"Expected file missing in {template_name}: {expected_file}"

#         # Check required directories from config
#         required_dirs = template_info.get("required_dirs", [])
#         for required_dir in required_dirs:
#             dir_path = project_path / required_dir
#             assert (
#                 dir_path.exists()
#             ), f"Required directory missing in {template_name}: {required_dir}"

#     @pytest.mark.parametrize("template_name", get_template_names.__func__())
#     def test_template_specific_features(
#         self, template_name: str, temp_dir: str, template_config: Dict[str, Any]
#     ) -> None:
#         """Test template-specific features based on configuration"""
#         template_info = template_config["templates"][template_name]

#         # Skip if no specific features to test
#         features_to_test = {
#             "docker_enabled",
#             "has_auth",
#             "has_database",
#             "test_endpoints",
#         }

#         if not any(feature in template_info for feature in features_to_test):
#             pytest.skip(f"No specific features to test for {template_name}")

#         # Create project first
#         project_name = f"feature-test-{template_name}"
#         # ... (create project using same logic as above)

#         project_path = Path(temp_dir) / project_name

#         # Test Docker features
#         if template_info.get("docker_enabled", False):
#             docker_files = ["Dockerfile", "docker-compose.yml"]
#             for docker_file in docker_files:
#                 assert (
#                     project_path / docker_file
#                 ).exists(), f"Docker file missing: {docker_file}"

#         # Test Authentication features
#         if template_info.get("has_auth", False):
#             auth_dir = project_path / "src" / "auth"
#             assert auth_dir.exists(), "Authentication directory missing"

#         # Test Database features
#         if template_info.get("has_database", False):
#             db_type = template_info.get("database_type", "")
#             if db_type == "postgresql":
#                 assert (
#                     project_path / "alembic.ini"
#                 ).exists(), "Alembic config missing for PostgreSQL"

#     def test_config_file_validity(self, template_config: Dict[str, Any]) -> None:
#         """Test that the configuration file is valid and complete"""
#         # Check required sections
#         assert "templates" in template_config, "Missing 'templates' section in config"
#         assert (
#             "global_settings" in template_config
#         ), "Missing 'global_settings' section in config"

#         templates = template_config["templates"]
#         assert len(templates) > 0, "No templates defined in config"

#         # Check each template has required fields
#         required_fields = ["description", "expected_files", "required_dirs"]
#         for template_name, template_info in templates.items():
#             for field in required_fields:
#                 assert (
#                     field in template_info
#                 ), f"Missing required field '{field}' in template '{template_name}'"

#             # Check that expected_files and required_dirs are lists
#             assert isinstance(
#                 template_info["expected_files"], list
#             ), f"expected_files must be a list in {template_name}"
#             assert isinstance(
#                 template_info["required_dirs"], list
#             ), f"required_dirs must be a list in {template_name}"

#     @pytest.mark.parametrize("template_name", get_template_names.__func__())
#     def test_template_consistency(
#         self, template_name: str, template_config: Dict[str, Any]
#     ) -> None:
#         """Test template consistency with actual file system"""
#         from fastapi_fastkit.core.settings import FastkitConfig

#         # Check if template actually exists in filesystem
#         settings = FastkitConfig()
#         template_path = Path(settings.FASTKIT_TEMPLATE_ROOT) / template_name

#         assert template_path.exists(), f"Template directory not found: {template_name}"
#         assert (
#             template_path.is_dir()
#         ), f"Template path is not a directory: {template_name}"

#         # Check that required template files exist
#         required_template_files = ["README.md-tpl", "setup.py-tpl"]
#         for required_file in required_template_files:
#             file_path = template_path / required_file
#             assert (
#                 file_path.exists()
#             ), f"Required template file missing in {template_name}: {required_file}"
