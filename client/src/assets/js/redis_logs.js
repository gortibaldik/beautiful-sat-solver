import { 
  mdbRow,
  mdbCol,
  mdbCard,
  mdbCardTitle,
  mdbCardBody,
  mdbScrollbar,
  mdbModal,
  mdbModalHeader,
  mdbModalFooter,
  mdbModalBody,
  mdbBtn,
  mdbModalTitle,
} from 'mdbvue'

import redis_logs from '@/assets/js/get_redis_logs'

export default {
  name: 'Profile',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardTitle,
    mdbCardBody,
    mdbScrollbar,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter,
    mdbModalBody,
    mdbBtn,
    mdbModalTitle,
  },
  data () {
    let basicMessage = "<code><strong>Nothing to show</strong></code>"
    return {
      errorLogs: basicMessage,
      stdLogs: basicMessage,
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
    }
  },
  methods: {
    async fetchRedisLogs() {
      let [errorLogs, stdLogs] = await redis_logs.fetch(this.serverAddress)
      this.errorLogs = errorLogs
      this.stdLogs = stdLogs
    },
    switchOnModalError() {
      this.displayModal = true
      this.modalMessage = this.errorLogs
      this.modalTitle = "Error Redis Worker Logs"
      this.modalInterval = setInterval(this.pollModalError.bind(this), 1000)
    },
    switchOnModalStd() {
      this.displayModal = true
      this.modalMessage = this.stdLogs
      this.modalTitle = "Standard Redis Worker Logs"
      this.modalInterval = setInterval(this.pollModalStd.bind(this), 1000)
    },
    async removeStdRedisLogs() {
      await redis_logs.fetch_remove_std(this.serverAddress)
    },
    async removeErrorRedisLogs() {
      await redis_logs.fetch_remove_error(this.serverAddress)
    },
    async pollLogs() {
      let [errorLogs, stdLogs] = await redis_logs.fetch(this.serverAddress)
      if (errorLogs === 'failure' && stdLogs === '') {
        clearInterval(this.pollingInterval)
        this.pollingInterval = undefined
        return
      }
      this.errorLogs = errorLogs
      this.stdLogs = stdLogs
    },
    pollModalError() {
      this.modalMessage = this.errorLogs
    },
    pollModalStd() {
      this.modalMessage = this.stdLogs
    },
    closeModal() {
      this.displayModal = false
      if (this.modalInterval) {
        clearInterval(this.modalInterval)
        this.modalInterval = undefined
      }
    },
    startMonitoringLogs() {
      this.pollingInterval = setInterval(this.pollLogs.bind(this), 1000)
    },
  },
  created() {
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    console.log(`server address: "${this.serverAddress}"`)
    this.fetchRedisLogs()
    this.startMonitoringLogs()
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = undefined
    }
    this.closeModal()
  }
}