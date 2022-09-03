import fetch_json from "@/assets/js/fetch_utils"

var custom_run = {
  async fetchBasicInfoFromServer(serverAddress) {
    return await fetch(`${serverAddress}/sudoku/`)
      .then(response => response.json())
  },
  async fetchStart(serverAddress, algo, sudoku, logLevel) {
    return await fetch_json.post(`${serverAddress}/sudoku/start`, {
      algorithm:        algo,
      sudoku:           sudoku,
      logLevel:         logLevel
    })
  },
  async fetchProgress(serverAddress, algo) {
    let data = null
    try {
      data = await fetch_json.post(`${serverAddress}/sudoku/is_finished`, {
        algorithm:        algo,
      })
    } catch {
      data = {
        result: 'failure'
      }
    }
    return data
  },
  async fetchStop(serverAddress, algo) {
    return await fetch_json.post(`${serverAddress}/sudoku/stop`, {
      algorithm:        algo,
    })
  },
  async fetchStdLogs(serverAddress, algo) {
    return await fetch_json.post(`${serverAddress}/sudoku/get_logs`, {
      algorithm:        algo,
    })
  },
  async fetchDimacsFile(serverAddress, algo) {
    return await fetch_json.post(`${serverAddress}/sudoku/get_dimacs`,  {
      algorithm:        algo,
    })
  },
  async fetchGenerateSudoku(serverAddress, difficulty) {
    let data = await fetch_json.post(`${serverAddress}/sudoku/generate`, {
      difficulty: difficulty
    })
    return data.board
  }
}

export default custom_run