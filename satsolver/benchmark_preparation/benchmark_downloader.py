import aiohttp
import asyncio
import os
import tarfile
import zipfile

from logzero import logger
from pathlib import Path
from satsolver.benchmark_preparation.filter_benchmark_files import filter_files
from server.config import Config
from shutil import rmtree

satlib_benchmark_urls = [
  ("http://ktiml.mff.cuni.cz/~kucerap/satsmt/practical/task1.zip", 5),
  # ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/GCP/flat30-60.tar.gz", 10),
  # ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/GCP/flat50-115.tar.gz", 10),
  # ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/GCP/flat75-180.tar.gz", 10),
  # ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/GCP/flat100-239.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz", 100),
  # ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf50-218.tar.gz", 50),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf50-218.tar.gz", 50),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf75-325.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf75-325.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf100-430.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf100-430.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf125-538.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf125-538.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf150-645.tar.gz", 10),
  ("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf150-645.tar.gz", 10)
]

def _construct_filename(base_filename, suffix_int, suffix_targz):
  return f"{base_filename}{suffix_int}{suffix_targz}"

def get_free_tmp_file(index):
  base_filename = "tmp"
  suffix_int = 1
  suffix_targz = ".zip" if satlib_benchmark_urls[index][0].endswith(".zip") else ".tar.gz"
  while os.path.isfile(_construct_filename(base_filename, suffix_int, suffix_targz)):
    suffix_int += 1
  
  return _construct_filename(base_filename, suffix_int, suffix_targz)

async def download_benchmark_to_memory(session, benchmark_index):
  url_to_download = satlib_benchmark_urls[benchmark_index][0]
  async with session.get(url_to_download) as resp:
    content = await resp.read()
    return content, benchmark_index

def remove_intermediate_folder(location_where_to_save):
  intermediate_location = location_where_to_save
  intermediate_locations = []

  while True:
    files = list(os.path.join(intermediate_location, f) for f in os.listdir(intermediate_location))
    if len(files) != 1:
      break
    intermediate_location = files[0]
    intermediate_locations = [intermediate_location] + intermediate_locations
  
  if intermediate_location == location_where_to_save:
    return
  
  for f in os.listdir(intermediate_location):
    os.rename(os.path.join(intermediate_location, f), os.path.join(location_where_to_save, f))
  
  for il in intermediate_locations:
    os.rmdir(il)

def extract(archive_file, location_where_to_save):
  if archive_file.endswith(".tar.gz"):
    with tarfile.open(archive_file) as file:
      file.extractall(location_where_to_save)
  elif archive_file.endswith(".zip"):
    with zipfile.ZipFile(archive_file, 'r') as zip_ref:
      zip_ref.extractall(location_where_to_save)

def process_downloaded_benchmark(downloaded_benchmark, benchmark_index, location_where_to_save):
  # the directory where the benchmark will be saved
  Path(location_where_to_save).mkdir(parents=True, exist_ok=True)
  
  # download the benchmark
  tmp_archive_file = get_free_tmp_file(benchmark_index)
  with open(tmp_archive_file, 'wb') as f:
    f.write(downloaded_benchmark)

  logger.info(f"Downloaded {satlib_benchmark_urls[benchmark_index][0]} to {tmp_archive_file}")

  extract(tmp_archive_file, location_where_to_save)

  os.remove(tmp_archive_file)
  remove_intermediate_folder(location_where_to_save)

  logger.info(f"Extracted {tmp_archive_file} to {location_where_to_save}")

async def download_and_preprocess_benchmark(benchmark_index, location_where_to_save):
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    downloaded_benchmark, _ = await download_benchmark_to_memory(session, benchmark_index)

  process_downloaded_benchmark(downloaded_benchmark, benchmark_index, location_where_to_save)
  filter_files(location_where_to_save, satlib_benchmark_urls[benchmark_index][1])
  logger.info(f"Filtered files in {location_where_to_save}")

def extract_directoryname_from_url(url):
  directoryname = url.strip().split("/")[-1].split(".")[0]
  return directoryname

def filter_downloaded_benchmarks(benchmark_root):
  if not os.path.isdir(benchmark_root):
    return [ (i, b, n) for i, (b, n) in enumerate(satlib_benchmark_urls)]
  dirs_in_benchmark_root = [ dir for dir in os.listdir(benchmark_root) if os.path.isdir(os.path.join(benchmark_root, dir)) ]
  
  filtered_benchmarks = []
  for i, (b, n) in enumerate(satlib_benchmark_urls):
    dirname = extract_directoryname_from_url(b)
    if dirname not in dirs_in_benchmark_root:
      filtered_benchmarks.append((i, b, n))
  
  for dirname in dirs_in_benchmark_root:
    is_present = False
    for i, (b, n) in enumerate(satlib_benchmark_urls):
      benchmark_name = extract_directoryname_from_url(b)
      if dirname == benchmark_name:
        is_present = True
        break
    if not is_present:
      logger.warning(f"REMOVED: {dirname}")
      rmtree(os.path.join(Config.SATSMT_BENCHMARK_ROOT, dirname))

  return filtered_benchmarks

async def download_all_not_downloaded_benchmarks():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  if not benchmark_root:
    benchmark_root = "benchmarks/"
  
  benchmarks_to_be_downloaded = filter_downloaded_benchmarks(benchmark_root)
  logger.info(f"Going to download: {benchmarks_to_be_downloaded}")

  # download all the benchmarks to memory
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    tasks = []
    for i, _, _ in benchmarks_to_be_downloaded:
      tasks.append(asyncio.ensure_future(download_benchmark_to_memory(session, i)))

    all_downloaded_benchmarks = await asyncio.gather(*tasks)
  
  # process benchmarks and extract them to benchmark_root
  for downloaded_benchmark, index in all_downloaded_benchmarks:
    benchmark_dir = os.path.join(
      benchmark_root,
      extract_directoryname_from_url(satlib_benchmark_urls[index][0])
    )
    process_downloaded_benchmark(
      downloaded_benchmark,
      index,
      benchmark_dir
    )
    filter_files(benchmark_dir, satlib_benchmark_urls[index][1])

if __name__ == "__main__":
  asyncio.run(download_all_not_downloaded_benchmarks())