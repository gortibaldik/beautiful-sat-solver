import fetch_json from "@/assets/js/fetch_utils"

var benchmark_communication = {
  async fetchRunningBenchmark(serverAddress) {
    return await fetch(`${serverAddress}/benchmarks/get_running_benchmark`)
        .then(response => response.json())
        .then(function(data) {
          if (data.result === "failure") {
            return ['none', 'none']
          }
          return [data.result.algorithm, data.result.benchmark]
        })
  },
  async fetchBenchmarkProgress(serverAddress, algo, bench) {
    return await fetch_json.post(`${serverAddress}/benchmarks/progress`, {
      algorithm: algo,
      benchmark: bench
    })
  },
  async fetchBenchmarks(serverAddress) {
    return await fetch(`${serverAddress}/benchmarks/`)
      .then(response => response.json())
  },
  async fetchBenchmarkResult(serverAddress, algorithm_name, benchmark_name) {
    return await fetch_json.post(`${serverAddress}/benchmarks/result`, {
      algorithm: algorithm_name,
      benchmark: benchmark_name
    })
  },
  async fetchStartBenchmark(serverAddress, algorithm_name, benchmark_name, log_level_name) {
    return await fetch_json.post(`${serverAddress}/benchmarks/start`, {
      algorithm: algorithm_name,
      benchmark: benchmark_name,
      logLevel:  log_level_name
    })
  },
  async fetchStopCommunication(serverAddress, algorithm_name, benchmark_name) {
    return await fetch_json.post(`${serverAddress}/benchmarks/stop`, {
      algorithm: algorithm_name,
      benchmark: benchmark_name
    })
  }
}

export default benchmark_communication