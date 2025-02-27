# --------------------------------------------------------------------------
# The Module transduces .*-tpl extension files to their respective file extensions
# and copies them to user's local directory.
#
# This will handle .py-tpl, .txt-tpl, .md-tpl, etc.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil


def _convert_tpl_to_real_extension(file_path: str) -> str:
    """
    Converts a file ending in `.*-tpl` to its respective file extension by removing the `-tpl` suffix.

    :param file_path: The full path of the `.*-tpl` file.
    :type file_path: str
    :return: The new path of the file with the `-tpl` suffix removed.
    """
    # Remove the '-tpl' suffix from any file extension
    if file_path.endswith("-tpl"):
        new_file_path = file_path.replace("-tpl", "")
        os.rename(file_path, new_file_path)
        return new_file_path
    return file_path


def copy_and_convert_template(
    template_dir: str, target_dir: str, project_name: str = ""
) -> None:
    """
    Copies all files from the template directory to the target directory,
    converting any files ending in `.*-tpl` during the copy process.

    :param project_name: name of new project user defined at CLI.
    :param template_dir: The source directory containing the template files.
    :type template_dir: str
    :param target_dir: The destination directory where files will be copied.
    :type target_dir: str
    """
    template_name = os.path.basename(template_dir)
    if project_name is None:
        project_name = template_name
    target_path = os.path.join(target_dir, project_name)
    os.makedirs(target_path, exist_ok=True)

    for root, dirs, files in os.walk(template_dir):
        relative_path = os.path.relpath(root, template_dir)
        destination_dir = os.path.join(target_path, relative_path)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        for file in files:
            src_file = os.path.join(root, file)

            if file.endswith("-tpl"):
                dst_file = os.path.join(destination_dir, file.replace("-tpl", ""))
                shutil.copy2(src_file, dst_file)
                _convert_tpl_to_real_extension(dst_file)
            else:
                dst_file = os.path.join(destination_dir, file)
                shutil.copy2(src_file, dst_file)


def copy_and_convert_template_file(
    source_file: str, target_file: str, replacements: dict = None  # type: ignore
) -> bool:
    """
    Copies a single template file to the target location, converting it from .*-tpl
    to its proper extension and replacing any placeholders with provided values.

    :param source_file: Path to the source template file (with -tpl extension)
    :param target_file: Path to target destination file (without -tpl extension)
    :param replacements: Dictionary of placeholder replacements {placeholder: value}
    :return: True if successful, False otherwise
    """
    try:
        if not os.path.exists(source_file):
            return False

        # Read a single source content (with .py-tpl extension)
        with open(source_file, "r") as src_file:
            content = src_file.read()

        if replacements and isinstance(replacements, dict):
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        with open(target_file, "w") as tgt_file:
            tgt_file.write(content)

        return True
    except Exception as e:
        print(f"Error copying template file: {e}")
        return False


def _convert_real_extension_to_tpl() -> None:
    # TODO : impl this for converting runnable FastAPI app code to template - debugging operation for contributors
    # this will be used at inspector module, not package user's runtime.
    pass
