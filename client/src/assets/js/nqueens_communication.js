import fetch_json from "@/assets/js/fetch_utils"

var custom_run = {
  async fetchBasicInfoFromServer(serverAddress) {
    return await fetch(`${serverAddress}/nqueens/`)
      .then(response => response.json())
  },
  async fetchStart(serverAddress, algo, n, run_as_benchmark, timeout, logLevel) {
    return await fetch_json.post(`${serverAddress}/nqueens/start`, {
      algorithm:        algo,
      N:                n,
      run_as_benchmark: run_as_benchmark,
      timeout:          timeout,
      logLevel:         logLevel
    })
  },
  async fetchProgress(serverAddress, algo, n, run_as_benchmark, timeout) {
    let data = null
    try {
      data = await fetch_json.post(`${serverAddress}/nqueens/is_finished`, {
        algorithm:        algo,
        N:                n,
        run_as_benchmark: run_as_benchmark,
        timeout:          timeout
      })
    } catch {
      data = {
        result: 'failure'
      }
    }
    return data
  },
  create_dict(algo, n, run_as_benchmark, timeout) {
    return {
      algorithm:        algo,
      N:                n,
      run_as_benchmark: run_as_benchmark,
      timeout:          timeout
    }
  },
  async fetchStop(serverAddress, algo, n, run_as_benchmark, timeout) {
    return await fetch_json.post(`${serverAddress}/nqueens/stop`,
      this.create_dict(algo, n, run_as_benchmark, timeout)
    )
  },
  async fetchStdLogs(serverAddress, algo, n, run_as_benchmark, timeout) {
    return await fetch_json.post(`${serverAddress}/nqueens/get_logs`,
      this.create_dict(algo, n, run_as_benchmark, timeout)
    )
  },
  async fetchDimacsFile(serverAddress, n) {
    return await fetch_json.post(`${serverAddress}/nqueens/get_dimacs`, {
      N: n
    })
  }
}

export default custom_run