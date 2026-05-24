from icrawler.builtin import BingImageCrawler
import os

# =========================================
# PASTAS
# =========================================

CAT_DIR = "dataset/images/train/cats"
DOG_DIR = "dataset/images/train/dogs"

os.makedirs(CAT_DIR, exist_ok=True)
os.makedirs(DOG_DIR, exist_ok=True)

# =========================================
# DOWNLOAD GATOS
# =========================================

print("Baixando imagens de gatos...")

cat_crawler = BingImageCrawler(
    storage={"root_dir": CAT_DIR}
)

cat_crawler.crawl(
    keyword="cats",
    max_num=20
)

# =========================================
# DOWNLOAD CACHORROS
# =========================================

print("Baixando imagens de cachorros...")

dog_crawler = BingImageCrawler(
    storage={"root_dir": DOG_DIR}
)

dog_crawler.crawl(
    keyword="dogs",
    max_num=20
)

print("Download finalizado!")