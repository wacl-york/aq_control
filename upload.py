#!/usr/bin/env python
"""#############################################################################
AWS S3 Bucket Upload
================================================================================
This requires AWS credentials to be set up in the user home directory.
#############################################################################"""
import argparse
import datetime
import glob
import gzip
import os
import sys

# ===============================================================================
import boto3

# ===============================================================================
def get_script_args():
    """
    Get command line arguments and options.
    """
    description = "Upload BOCS data to AWS S3 bucket"
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument(
        "site_name",
        metavar="site_name",
        nargs=1,
        type=str,
        help="Name of remote monitoring site",
    )
    help_string = "Path of directory in which to find data to upload"
    arg_parser.add_argument(
        "data_directory",
        metavar="data_directory",
        nargs=1,
        type=str,
        help=help_string,
    )
    return arg_parser.parse_args()


def compress_file(filename):
    """
    gzip the file that we are going to transfer to S3.
    """
    outfile_name = f"{filename}.gz"
    with open(filename, "rb") as infile, gzip.open(
        outfile_name, "wb"
    ) as outfile:
        outfile.writelines(infile)

    return outfile_name


def file_to_upload(directory):
    """
    Get the file to be uploaded to AWS, looking for yesterday's date in the
    filename and a .log extension.
    """
    absolute_directory = os.path.abspath(directory)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date_string = (
        f"{yesterday.year}-{str(yesterday.month).zfill(2)}-"
        f"{str(yesterday.day).zfill(2)}"
    )
    glob_pattern = os.path.join(absolute_directory, f"*{date_string}*.log")
    candidate = glob.glob(glob_pattern)

    if not candidate:
        error_string = "ERROR: UNABLE TO FIND YESTERDAY'S DATA FILE!\n"
        raise RuntimeError(error_string)

    if len(candidate) > 1:
        error_string = "ERROR: MULTIPLE DATA FILES FOUND FOR YESTERDAY!\n"
        raise RuntimeError(error_string)

    return candidate[0]


# ===============================================================================
def main():
    """
    Main entry point for this script.
    """
    script_args = get_script_args()

    profile_name = f"bocs-remote-upload-{script_args.site_name[0]}"
    try:
        data_file = file_to_upload(script_args.data_directory[0])
    except RuntimeError as exception:
        sys.stderr.write(str(exception))
        sys.exit(1)

    compressed_data_file = compress_file(data_file)

    object_key = os.path.join(
        script_args.site_name[0], os.path.basename(compressed_data_file)
    )
    info_string = (
        f"INFO: UPLOADING {compressed_data_file} TO {object_key} IN BUCKET\n"
    )
    sys.stderr.write(info_string)

    session = boto3.session.Session(profile_name=profile_name)
    sss = session.resource("s3")

    sss.Bucket("bocs-remote-uploads").upload_file(
        compressed_data_file, object_key
    )

    # TODO: IF UPLOAD IS SUCCESSFUL, DELETE UNCOMPRESSED DATA FROM PI

    sys.exit(0)


# ===============================================================================
if __name__ == "__main__":
    main()
