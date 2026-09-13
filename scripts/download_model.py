import os
import shutil

from huggingface_hub import snapshot_download


MODEL_ID = "ai4bharat/indictrans2-en-indic-dist-200M"

OUTPUT_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "models",
    "indictrans2-en-indic-dist-200M"
)


def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("=" * 70)
    print("Downloading IndicTrans2 English → Indic 200M")
    print("=" * 70)

    print("Model:")
    print(MODEL_ID)

    print()
    print("Destination:")
    print(OUTPUT_DIR)

    print()

    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=OUTPUT_DIR,
        local_dir_use_symlinks=False
    )

    print()
    print("=" * 70)
    print("MODEL DOWNLOAD COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
