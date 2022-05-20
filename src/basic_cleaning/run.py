#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     # 
    logger.info("locating and reading the artifact")
    df = pd.read_csv(artifact_local_path)

    # Drop outliers
    logger.info("dropping the outliers and making other corrections")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    
    logger.info("locally saving the cleaned sample")
    df.to_csv(args.output_artifact, index=False)


    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )

    logger.info("loading and logging the saved clean sample")
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    logger.info("deleting local saves and ending run")
    os.remove(args.output_artifact)
    run.finish()

    ######################


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="wandb input artifact e.g., sample.csv:latest",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="output artifact filename e.g., clean_sample.csv",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="defining term for output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=int,
        help="lowest value below which outliers exist",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=int,
        help="highest value below which outliers exist",
        required=True
    )


    args = parser.parse_args()

    go(args)
