# --------------------------------------------------------------------------
# The Module transduces .py-tpl extension files to .py at fastapi template
# and copies them to user's local directory.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil


def convert_py_tpl_to_py(file_path: str) -> str:
    """
    Converts a .py-tpl file to .py by renaming the file.

    :param file_path: The full path of the .py-tpl file.
    :return: The new path of the .py file.
    """
    py_path = file_path.replace(".py-tpl", ".py")
    os.rename(file_path, py_path)
    return py_path


def copy_and_convert_template(template_dir: str, target_dir: str) -> None:
    """
    Copies all files from the template directory to the target directory,
    converting .py-tpl files to .py during the copy process.

    :param template_dir: The source directory containing the template files.
    :param target_dir: The destination directory where files will be copied.
    """
    template_name = os.path.basename(template_dir)
    target_path = os.path.join(target_dir, template_name)
    os.makedirs(target_path, exist_ok=True)

    for root, _, files in os.walk(template_dir):
        relative_path = os.path.relpath(root, template_dir)
        destination_dir = os.path.join(target_path, relative_path)

        for file in files:
            src_file = os.path.join(root, file)

            if file.endswith(".py-tpl"):
                dst_file = os.path.join(destination_dir, file.replace(".py-tpl", ".py"))
                shutil.copy2(src_file, dst_file)
                convert_py_tpl_to_py(dst_file)
            else:
                dst_file = os.path.join(destination_dir, file)
                shutil.copy2(src_file, dst_file)
