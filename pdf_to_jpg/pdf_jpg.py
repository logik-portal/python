# PDF to JPG
# Copyright (c) 2025 Michael Vaglienty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: PDF to JPG
Script Version: 1.0.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 01.04.26
Update Date: 01.04.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Media Panel

Description:

    Convert a PDF file to a series of JPG images.

    Image Layout Options:
        - Single: 1 page per image
        - 2-up Horizontal: 2 pages per image, side-by-side
        - 2-up Vertical: 2 pages per image, top/bottom
        - Grid 2x2: 4 pages per image in a 2x2 grid

    Images can be imported into a Flame library and revealed in MediaHub or Finder.

    Image path is copied to clipboard and can be pasted into other applications.

Menus:

    Right-click in Media Panel -> PDF to JPG

To install:

    Copy script into /opt/Autodesk/shared/python/pdf_to_jpg

Updates:

    v1.0.0 01.04.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import flame
from lib.pyflame_lib_pdf_to_jpg import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'PDF to JPG'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class PDFtoJPG:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Install required python packages if not already installed.
        if not self.install_required_python_packages():
            return

        # Create/Load config file settings.
        self.load_config()

        # Get PDF path
        pdf_path = self.get_pdf_path()
        if not pdf_path:
            return

        # Convert PDF to JPG
        self.conversion_window(pdf_path)

    def install_required_python_packages(self) -> bool:
        """
        Install Required Python Packages
        ================================

        Install the required python packages for the script.

        Returns
        -------
            bool:
                True if the python packages are installed, False otherwise.
        """

        # Install required python packages if not already installed.
        flame_version = pyflame.get_flame_version()

        # Determine which Python version is required.
        if flame_version <= 2026.9:
            python_version = '3.11'
        elif flame_version >= 2027.0 and flame_version < 2027.9:
            python_version = '3.13'
        else:
            PyFlameMessageWindow(
                message=f'Flame version: {flame_version} is not supported.',
                message_type=MessageType.ERROR,
                title='PDF to JPG',
                parent=None,
                )
            return False

        # Install required python packages
        installed = pyflame.python_package_local_install(package=[f'PIL_python{python_version}', 'fitz'])
        if not installed:
            pyflame.print(f'Python packages not installed, exiting script.')
            return False
        return True

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads configuration values from the config file and applies them to `self.settings`.

        If the config file does not exist, it creates the file using the default values
        from the `config_values` dictionary. Otherwise, it loads the existing config values
        and applies them to `self.settings`.
        """

        self.settings = PyFlameConfig(
            config_values={
                'pdf_path': '/opt/Autodesk',
                'layout': 'Single',
                'image_resolution': 150,
                'add_page_numbers': True,
                'import_jpgs': True,
                'reveal_in_mediahub': False,
                'reveal_in_finder': False,
                },
            )

    # ------------------------------------------------------------------------------

    def get_pdf_path(self) -> str:
        """
        Get PDF Path
        ============

        Open a Flame file browser to select the PDF file to convert.

        Returns
        -------
            str:
                Path to the PDF file to convert.
                If no path is selected, returns `None`.
        """

        pdf_path = pyflame.file_browser(
                    path=self.settings.pdf_path,
                    title=f'Select PDF to convert',
                    extension='pdf',
                    )

        if not pdf_path:
            pyflame.print(f'No PDF path selected, exiting script.')
            return None

        # Check file header to ensure it's actually a PDF file (not an image with PDF extension)
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    PyFlameMessageWindow(
                        message=f'Invalid PDF file:\n\n{pdf_path}\n\nFile does not have PDF header',
                        message_type=MessageType.ERROR,
                        title='PDF to JPG',
                        parent=None,
                        )
                    return None
        except IOError:
            PyFlameMessageWindow(
                message=f'Invalid PDF file:\n\n{pdf_path}\n\nCannot read file',
                message_type=MessageType.ERROR,
                title='PDF to JPG',
                parent=None,
                )
            return None

        pyflame.print(f'PDF path: {pdf_path}')

        return pdf_path

    def conversion_window(self, pdf_path: str) -> None:
        """
        Conversion Window
        =================

        Open a window to convert the PDF file to JPG images.

        Args
        ----
            pdf_path (str):
                Path to the PDF file to convert.
        """

        def convert_pdf_to_jpg() -> None:
            """
            Convert PDF to JPG
            ==================

            Convert the PDF file to JPG images.

            Saves config, converts PDF to JPG, copies output directory to clipboard,
            imports JPGs into Flame library (if enabled), and opens output directory in MediaHub or Finder (if enabled).
            """

            # Save config
            save_config()

            # Convert PDF to JPG
            output_dir = pdf_conversion()

            # Copy output directory to clipboard
            print(f'JPG Export Path: {output_dir}')
            pyflame.copy_to_clipboard(output_dir)

            # Set Progress Window Tasks Complete
            self.progress_window.tasks_completed(
                done_button_enabled=False
                )

            # Import JPGs into Flame library (if enabled)
            if self.settings.import_jpgs:
                self.progress_window.title = 'PDF to JPG: Importing JPGs'
                import_jpgs(output_dir)
            else:
                self.progress_window.text_append(f'Conversion complete. JPGs exported to:\n\n{output_dir}')
            self.progress_window.enable_done_button()

            # Reveal output directory in MediaHub or Finder
            if self.settings.reveal_in_mediahub:
                flame.go_to('MediaHub')
                flame.mediahub.files.set_path(output_dir)
                pyflame.print(f'Path opened in MediaHub: {output_dir}', text_color=TextColor.GREEN)
            if self.settings.reveal_in_finder:
                pyflame.open_in_finder(path=output_dir)
                pyflame.print(f'Path opened in Finder: {output_dir}', text_color=TextColor.GREEN)

        def save_config() -> None:
            """
            Save Config
            ===========

            Save windowsettings to config file.
            """

            self.settings.save_config(
                config_values={
                    'pdf_path': pdf_path,
                    'layout': self.layout_menu.text,
                    'image_resolution': self.image_resolution_slider.value,
                    'add_page_numbers': self.add_page_numbers_push_button.checked,
                    'import_jpgs': self.import_jpgs_push_button.checked,
                    'reveal_in_mediahub': self.reveal_in_mediahub_push_button.checked,
                    'reveal_in_finder': self.reveal_in_finder_push_button.checked,
                    }
                )

            self.window.close()

        def pdf_conversion() -> str:
            """
            PDF Conversion
            ==============

            Convert a PDF file to a series of JPG images, optionally combining multiple
            pages into a single output image with or without page numbers.

            Returns
            -------
                str:
                    Path to the output directory.
            """

            def render_page_to_pil(page_index: int) -> Image.Image:
                """
                Render Page to PIL
                ==================

                Render a single PDF page to a PIL RGB image (in memory).

                Args
                ----
                    page_index (int):
                        Index of the page to render.

                Returns
                -------
                    Image.Image:
                        PIL RGB image of the rendered page.
                """

                page = pdf_document[page_index]
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
                return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

            def add_page_number(image: Image.Image, page_num: int) -> Image.Image:
                """
                Add Page Number
                ===============

                Draw a page number on the image.

                Args
                ----
                    image (Image.Image):
                        PIL image to annotate.
                    page_num (int):
                        Page number to display (1-indexed).

                Returns
                -------
                    Image.Image:
                        PIL image with page number added.
                """
                from PIL import ImageDraw, ImageFont

                # Create a copy to avoid modifying the original
                img = image.copy()
                draw = ImageDraw.Draw(img)

                # Calculate font size based on image dimensions (approximately 2% of height)
                font_size = max(12, int(img.height * 0.02))

                try:
                    # Try to use a default font, fallback to default if not available
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                except:
                    try:
                        font = ImageFont.load_default()
                    except:
                        font = None

                # Page number text
                text = f"Page {page_num}"

                # Calculate text position (bottom-right corner with padding)
                if font:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    # Fallback if font loading fails
                    text_width = len(text) * 6
                    text_height = 12

                padding = int(img.width * 0.01)  # 1% padding
                x = img.width - text_width - padding
                y = img.height - text_height - padding

                # Draw a white background rectangle for better visibility
                bg_padding = 4
                draw.rectangle(
                    [x - bg_padding, y - bg_padding, x + text_width + bg_padding, y + text_height + bg_padding],
                    fill=(255, 255, 255)
                )

                # Draw the page number text
                draw.text((x, y), text, fill=(0, 0, 0), font=font)

                return img

            def combine_images(images: list[Image.Image]) -> Image.Image:
                """
                Combine Images
                ==============

                Combine rendered page images into a single canvas.
                Pages are padded (not scaled) into equal-sized cells based on max width/height
                in the current group, centered within each cell.

                Args
                ----
                    images (list[Image.Image]):
                        List of PIL RGB images to combine.

                Returns
                -------
                    Image.Image:
                        PIL RGB image of the combined canvas.
                """

                if not images:
                    pyflame.raise_value_error('combine_images', 'images', 'list[Image.Image]', images)

                cell_w = max(im.width for im in images)
                cell_h = max(im.height for im in images)

                canvas_w = cell_w * cols
                canvas_h = cell_h * rows

                canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')

                for idx, im in enumerate(images):
                    r = idx // cols
                    c = idx % cols
                    if r >= rows:
                        break

                    # Center image in its cell (padding)
                    x0 = c * cell_w + (cell_w - im.width) // 2
                    y0 = r * cell_h + (cell_h - im.height) // 2
                    canvas.paste(im, (x0, y0))

                return canvas

            def open_progress_window() -> None:
                """
                Open Progress Window
                ====================

                Open a progress window to display the progress of the PDF conversion.
                """

                # Open Progress Window
                self.progress_window = PyFlameProgressWindow(
                    total_tasks=total_output_images,  # Use output image count
                    title='PDF to JPG: Converting PDF to JPGs',
                    parent=None,
                    )

            layout = self.settings.layout
            #print(f'Layout: {layout}')

            # --- layout configuration ---
            if layout == 'Single':
                pages_per_image, cols, rows = 1, 1, 1
            elif layout == '2-up Horizontal':
                pages_per_image, cols, rows = 2, 2, 1
            elif layout == '2-up Vertical':
                pages_per_image, cols, rows = 2, 1, 2
            elif layout == 'Grid 2x2':
                pages_per_image, cols, rows = 4, 2, 2

            # Get PDF file name without extension
            pdf_name = os.path.splitext(os.path.basename(self.settings.pdf_path))[0]
            output_dir = os.path.join(os.path.dirname(self.settings.pdf_path), f'{pdf_name}_JPG_Export')
            print(f'Output directory: {output_dir}')
            if os.path.exists(output_dir):
                # Delete output directory
                shutil.rmtree(output_dir)
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Open PDF
            pdf_document = fitz.open(self.settings.pdf_path)
            total_pdf_pages = len(pdf_document)  # Keep original count for looping
            print(f'Total PDF pages: {total_pdf_pages}')

            # Calculate number of output images (for progress tracking)
            total_output_images = (total_pdf_pages + pages_per_image - 1) // pages_per_image  # Round up
            print(f'Total output images: {total_output_images}')

            dpi = self.settings.image_resolution

            pyflame.print(f'Converting PDF: {pdf_name} ({total_pdf_pages} pages) to JPG images at {dpi} DPI using layout: {layout}...')

            # zoom factor = dpi / 72 (default PDF DPI)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            # Open Progress Window
            open_progress_window()
            pages_processed = 1 # Initialize pages processed

            # Convert pages in groups - loop over actual PDF pages
            out_index = 0
            for start in range(0, total_pdf_pages, pages_per_image):  # Use total_pdf_pages, not total_output_images
                self.progress_window.current_task = pages_processed

                # Get the actual page indices to process from the PDF
                group_indices = list(range(start, min(start + pages_per_image, total_pdf_pages)))
                rendered = [render_page_to_pil(i) for i in group_indices]

                # Add page numbers to each rendered page if enabled
                if self.settings.add_page_numbers:
                    rendered_with_numbers = [add_page_number(img, idx + 1) for img, idx in zip(rendered, group_indices)]
                else:
                    rendered_with_numbers = rendered

                if pages_per_image == 1:
                    combined = rendered_with_numbers[0]
                    page_label = f"{group_indices[0] + 1:03d}"
                else:
                    combined = combine_images(rendered_with_numbers)
                    page_label = f"{group_indices[0] + 1:03d}-{group_indices[-1] + 1:03d}"

                out_index += 1
                output_filename = f"{pdf_name}_{out_index:03d}_pages_{page_label}.jpg"
                output_path = os.path.join(output_dir, output_filename)

                combined.save(output_path, 'JPEG', quality=100)

                # Update Progress
                pages_processed += 1

            pdf_document.close()

            # Update Progress Window
            self.progress_window.title = 'PDF to JPG: Conversion Complete'

            print('\n')
            return output_dir

        def import_jpgs(output_dir: str) -> None:
            """
            Import JPGs
            ===========

            Create a new Flame library and import the JPGs into it.

            Args
            ----
                output_dir (str):
                    Path to the output directory.
            """

            pyflame.print('Importing JPGs...', underline=True, new_line=False)
            pyflame.print(f'Output directory: {output_dir}', new_line=False)
            pyflame.print('Creating Flame library...', new_line=False)

            self.progress_window.text_append(f'Conversion complete. Importing JPGs into Flame. Please wait...')

            # Create a new Flame library
            import_library = flame.projects.current_project.current_workspace.create_library('-= Imported PDF Images =-')
            import_library.expanded = True

            pyflame.print('Importing JPGs into library...', new_line=False)

            # Set Progress Window Tasks Complete
            # Import JPGs into Flame library
            for file in os.listdir(output_dir):
                if file.endswith('.jpg'):
                    flame.import_clips(os.path.join(output_dir, file), import_library)

            pyflame.print('JPG import complete.')
            self.progress_window.text_append(f'JPG import complete.')
            self.progress_window.title = 'PDF to JPG: Import Complete'

        def close_window() -> None:

            self.window.close()

        # ==============================================================================
        # [Imports] - keep these imports local to this function.
        # ==============================================================================

        from PIL import Image
        import pymupdf as fitz

        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=convert_pdf_to_jpg,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=5,
            grid_layout_adjust_column_widths={2: 50},
            parent=None,
            )

        # Labels
        self.pdf_path_label = PyFlameLabel(
            text='PDF Path',
            )
        self.layout_label = PyFlameLabel(
            text='Image Layout',
            )
        self.image_resolution_label = PyFlameLabel(
            text='Image Resolution (DPI)',
            )

        # Entries
        self.pdf_path_entry = PyFlameEntry(
            text=pdf_path,
            read_only=True,
            )

        # Sliders
        self.image_resolution_slider = PyFlameSlider(
            min_value=100,
            max_value=300,
            start_value=self.settings.image_resolution,
            )

        # Menus
        self.layout_menu = PyFlameMenu(
            text=self.settings.layout,
            menu_options=[
                'Single',
                '2-up Horizontal',
                '2-up Vertical',
                'Grid 2x2',
                ],
            )

        # Push Buttons
        self.reveal_in_mediahub_push_button = PyFlamePushButton(
            text='Reveal in MediaHub',
            checked=self.settings.reveal_in_mediahub,
            )
        self.reveal_in_finder_push_button = PyFlamePushButton(
            text='Reveal in Finder',
            checked=self.settings.reveal_in_finder,
            )
        self.add_page_numbers_push_button = PyFlamePushButton(
            text='Add Page Numbers',
            checked=self.settings.add_page_numbers,
            )
        self.import_jpgs_push_button = PyFlamePushButton(
            text='Import JPGs',
            checked=self.settings.import_jpgs,
            )

        # Buttons
        self.convert_button = PyFlameButton(
            text='Convert',
            connect=convert_pdf_to_jpg,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ==============================================================================
        # [Widget Layout]
        # ==============================================================================

        self.window.grid_layout.addWidget(self.pdf_path_label, 0, 0)
        self.window.grid_layout.addWidget(self.pdf_path_entry, 0, 1, 1, 4)

        self.window.grid_layout.addWidget(self.layout_label, 1, 0)
        self.window.grid_layout.addWidget(self.layout_menu, 1, 1)

        self.window.grid_layout.addWidget(self.image_resolution_label, 1, 3)
        self.window.grid_layout.addWidget(self.image_resolution_slider, 1, 4)

        self.window.grid_layout.addWidget(self.reveal_in_mediahub_push_button, 3, 0)
        self.window.grid_layout.addWidget(self.reveal_in_finder_push_button, 3, 1)

        self.window.grid_layout.addWidget(self.add_page_numbers_push_button, 3, 3)
        self.window.grid_layout.addWidget(self.import_jpgs_push_button, 3, 4)

        self.window.grid_layout.addWidget(self.cancel_button, 5, 3)
        self.window.grid_layout.addWidget(self.convert_button, 5, 4)

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'PDF to JPG',
                    'order': 1,
                    'separator': 'below',
                    'execute': PDFtoJPG,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
