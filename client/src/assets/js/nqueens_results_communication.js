import fetch_json from "@/assets/js/fetch_utils"

var results_communication = {
  async fetchBenchmarkResults(serverAddress) {
    return await fetch(`${serverAddress}/nqueens_results/`)
      .then(response => response.json())
  },
  async fetchLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}/nqueens_results/get_log_file`, {
      log_file: log_file
    })
  },
  async fetchDeleteLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}/nqueens_results/remove_log_file`, {
      log_file: log_file
    })
  }
}

export default results_communication