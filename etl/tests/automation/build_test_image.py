import subprocess
import os


def clone_github_repo(github_url, repo_name):
    try:
        print("Cloning the GitHub repository...")
        subprocess.run(["git", "clone", github_url, repo_name], check=True)
        print("Repository cloned successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to clone the repository: {e}")
        return False
    return True


def build_docker_image(repo_name, image_name):
    try:
        print("Building the Docker image...")
        os.chdir(repo_name)
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)
        print("Docker image built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to build the Docker image: {e}")
        return False
    return True


if __name__ == "__main__":
    # github_url = "https://github.com/vfeskov/gitpunch.git"
    # image_name = "scribe2_gitpunch_test"

    # read the vars from the environment variables
    github_url = os.environ.get("TEST_IMAGE_GITHUB_URL")
    image_name = os.environ.get("TEST_IMAGE_NAME")
    repo_name = os.environ.get("TEST_REPO_DIR")

    if clone_github_repo(github_url, repo_name):
        build_docker_image(repo_name, image_name)
