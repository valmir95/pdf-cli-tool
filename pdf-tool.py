import argparse
import os
import PyPDF2

# Parse command line arguments
parser = argparse.ArgumentParser(description="Split or merge PDF files.")
subparsers = parser.add_subparsers(
    dest="command", help="Choose an operation to perform."
)

simple_parser = subparsers.add_parser(
    "simple",
    help="Interactive mode which allows you to choose the operation and arguments interactively.",
)

split_parser = subparsers.add_parser(
    "split", help="Split a PDF file into separate pages."
)
split_parser.add_argument(
    "-i", "--input", help="the path to the input PDF file which you want to split."
)
split_parser.add_argument(
    "-o",
    "--output",
    help="the path to the output file or directory where the extracted pages should be saved",
)
split_parser.add_argument(
    "-s",
    "--start",
    type=int,
    default=1,
    help="the starting page number (inclusive) of the range of pages to extract (default: 1)",
)
split_parser.add_argument(
    "-e",
    "--end",
    type=int,
    help="the ending page number (inclusive) of the range of pages to extract",
)
split_parser.add_argument(
    "-m",
    "--merge",
    action="store_true",
    help="a flag that determines whether to merge the extracted pages into a single PDF file (default: False)",
)

merge_parser = subparsers.add_parser(
    "merge", help="Merge multiple PDF files into a single PDF."
)
merge_parser.add_argument(
    "--inputs", nargs="+", help="a list of input PDF files to merge."
)
merge_parser.add_argument(
    "--output", help="the path to the output file where the merged PDF should be saved"
)
args = parser.parse_args()


def get_pdf_page_count(input_path):
    # Open the PDF file
    with open(input_path, "rb") as input_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(input_file)
        # Return the number of pages in the PDF file
        return len(pdf_reader.pages)


def extract_pdf_pages(input_path, output_path, start_page, end_page, merge):
    # Open the PDF file
    with open(input_path, "rb") as input_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(input_file)

        # Create a PDF writer object
        pdf_writer = PyPDF2.PdfWriter()

        # Loop through the range of pages and add each page to the PDF writer
        for page_num in range(start_page, end_page + 1):
            page = pdf_reader.pages[page_num - 1]
            pdf_writer.add_page(page)

        # Write the extracted pages to a new PDF file or files
        if merge:
            if (
                output_path
                and os.path.dirname(output_path)
                and not os.path.exists(output_path)
            ):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Merge the extracted pages into a single PDF file
            if not output_path or os.path.isdir(output_path):
                output_path += os.path.splitext(input_path)[0] + "_merged.pdf"

            if not output_path.lower().endswith(".pdf"):
                output_path += ".pdf"
            with open(output_path, "wb") as output_file:
                pdf_writer.write(output_file)
                print("Split and merged to: " + output_path)
        else:
            if start_page - end_page != 0 and not os.path.exists(output_path):
                os.makedirs(output_path)
            for i, page in enumerate(pdf_writer.pages):
                page_output_path = os.path.join(output_path, f"page_{i+start_page}.pdf")
                if output_path.lower().endswith(".pdf") and start_page - end_page == 0:
                    page_output_path = output_path

                with open(page_output_path, "wb") as page_output_file:
                    page_writer = PyPDF2.PdfWriter()
                    page_writer.add_page(page)
                    page_writer.write(page_output_file)
            print("Split the files into the following dir: " + output_path)


def get_pdf_files_from_directory(directory_path):
    pdf_files = [
        os.path.join(directory_path, filename)
        for filename in os.listdir(directory_path)
        if filename.lower().endswith(".pdf")
    ]
    return pdf_files


def merge_pdfs(input_paths, output_path):
    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()
    pdf_files = []

    # Loop through each input PDF and add its pages to the PDF writer
    for input_path in input_paths:
        if os.path.isdir(input_path):
            pdf_files.extend(get_pdf_files_from_directory(input_path))
        elif input_path.lower().endswith(".pdf"):
            pdf_files.append(input_path)

    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

    # Write the merged PDF to the output file
    with open(output_path, "wb") as output_file:
        pdf_writer.write(output_file)
        print("Merged the files to: " + output_path)


def init_merge():
    if not args.inputs:
        merge_parser.print_help()
        return
    if not args.output:
        args.output = "documents_merged.pdf"
    merge_pdfs(args.inputs, args.output)


def init_split():
    if not args.input:
        split_parser.print_help()
        return
    if not args.end:
        args.end = get_pdf_page_count(args.input)
    if not args.output:
        if args.merge:
            args.output = (
                os.path.splitext(args.input)[0]
                + "-pages_"
                + str(args.start)
                + "_to_"
                + str(args.end)
                + "_merged.pdf"
            )
        else:
            args.output = (
                os.path.splitext(args.input)[0]
                + "-pages_"
                + str(args.start)
                + "_to_"
                + str(args.end)
            )
    extract_pdf_pages(args.input, args.output, args.start, args.end, args.merge)


def init_simple():
    choice = input("Do you want to split or merge? ")
    if choice == "split":
        args.input = input("Enter the input file name/path: ")
        args.output = input("Enter the output file name/path: ")
        args.start = input(
            "Enter the starting page to split from (1-"
            + str(get_pdf_page_count(args.input))
            + ")"
        )
        args.end = input(
            "Enter the end page you want to split to (1-"
            + str(get_pdf_page_count(args.input))
            + ")"
        )
        args.merge = input(
            "Do you want to merge the extracted pages into a single PDF? (yes/no): "
        )
        args.start = int(args.start) if args.start else 1
        args.end = int(args.end) if args.end else None
        args.output = args.output if args.output else None
        args.merge = True if args.merge.lower() == "yes" else False
        init_split()
    elif choice == "merge":
        args.inputs = input(
            "Enter the input file paths, separated by a single space: "
        ).split(" ")
        args.output = input("Enter the output file path: ")
        init_merge()
    else:
        print("Invalid choice. Please choose either 'split' or 'merge'.")


if args.command != "split" and args.command != "merge" and args.command != "simple":
    parser.print_help()
else:
    if args.command == "merge":
        init_merge()
    elif args.command == "split":
        init_split()
    elif args.command == "simple":
        init_simple()
