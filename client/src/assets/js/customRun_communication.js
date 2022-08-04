import fetch_json from "@/assets/js/fetch_utils"

var custom_run = {
  async fetchStart(serverAddress, algo, bench, benchIn, logLevel) {
    return await fetch_json.post(`${serverAddress}/custom_run/start`, {
        algorithm:  algo,
        benchmark:  bench,
        entry:      benchIn,
        logLevel:   logLevel
    })
  },
  async fetchStop(serverAddress, algo, bench, benchIn) {
    return await fetch_json.post(`${serverAddress}/custom_run/stop`, {
      algorithm: algo,
      benchmark: bench,
      entry:     benchIn
    })
  },
  async fetchProgress(serverAddress, algo, bench, benchIn) {
    let data = null
    try {
      data = await fetch_json.post(`${serverAddress}/custom_run/is_finished`, {
          algorithm:  algo,
          benchmark:  bench,
          entry:      benchIn
      })
    } catch {
      data = {
        result: 'failure'
      }
    }
    return data.result
  },
  async fetchBasicInfoFromServer(serverAddress) {
    let data = await fetch(`${serverAddress}/custom_run/`)
      .then(response => response.json())
    return [data.benchmarks, data.algorithms, data.running_job]
  },
  async fetchCustomRunLogs(serverAddress) {
    let data = await fetch(`${serverAddress}/custom_run/get_logs`)
      .then(response => response.json())
    return data.result
  },
  async fetchRunningCustomRun(serverAddress) {
    return await fetch(`${serverAddress}/custom_run/get_running_custom_run`)
      .then(response => response.json())
  },
  async fetchBenchmarkInput(serverAddress, bench, benchIn) {
    return await fetch_json.post(`${serverAddress}/custom_run/show_benchmark`, {
      benchmark: bench,
      entry:     benchIn
    })
  }
}

export default custom_run