import psycopg2
import json
import argparse
from pathlib import Path


def load_images_from_file(file):
    print(file)
    with open(file) as fd:
        data = json.load(fd)

    images = []
    for repo, tags in data.items():
        for tag, imgs in tags.items():
            for img in imgs:
                image = {
                    "image_id": img["image_id"],
                    "digest": img["digest"],
                    "repository": repo,
                    "tag": tag,
                    "layers": img["layers"],
                    "config": json.dumps(img["config"]),
                    "registry_scan_config": 1,
                    "state": "in_progress",  # temp workaround
                }
                images.append(image)
    return images


def add_images_to_table(conn, images):
    try:
        with conn.cursor() as cur:
            columns = ",".join(images[0].keys())
            values = ",".join(
                cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", [*i]).decode("utf-8")
                for i in [image.values() for image in images]
            )
            q = f"""INSERT INTO osint."RegistryImage" ({columns}) VALUES {values}"""
            cur.execute(q)
            conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        print(e)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True, help="postgres port")
    parser.add_argument("-c", "--credentials", required=True, help='postgres "user:password"')
    parser.add_argument("-f", "--file", help="process a single file")
    parser.add_argument("-d", "--dir", help="process all files in a directory")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
    else:
        user, password = args.credentials.split(":")
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=args.port,
                dbname="airflow",
                user=user,
                password=password,
            )
            if args.file:
                images = load_images_from_file(args.file)
                add_images_to_table(conn, images)
            elif args.dir:
                for file in list(Path(args.dir).glob("*.json")):
                    images = load_images_from_file(file)
                    add_images_to_table(conn, images)
        finally:
            conn.close()
