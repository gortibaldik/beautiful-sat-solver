import { 
  mdbRow,
  mdbCol,
  mdbCard,
  mdbCardBody,
} from 'mdbvue'

import redis_logs from '@/assets/js/get_redis_logs'
import ModalCard from '@/components/ModalCard.vue'
import Vue from 'vue'

export default {
  name: 'RedisLogs',
  title: 'SAT: Logs',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardBody,
    ModalCard,
  },
  data () {
    let basicMessage = "<code><strong>Nothing to show</strong></code>"
    return {
      errorLogs: {
        data: basicMessage
      },
      stdLogs: {
        data: basicMessage
      },
    }
  },
  methods: {
    async fetchRedisLogs() {
      let [errorLogs, stdLogs] = await redis_logs.fetch(this.serverAddress)
      Vue.set(this.errorLogs, "data", errorLogs)
      Vue.set(this.stdLogs, "data", stdLogs)
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
      Vue.set(this.errorLogs, "data", errorLogs)
      Vue.set(this.stdLogs, "data", stdLogs)
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
    this.removeErrorRedisLogsBinded = this.removeErrorRedisLogs.bind(this)
    this.removeStdRedisLogsBinded = this.removeStdRedisLogs.bind(this)
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = undefined
    }
    this.closeModal()
  }
}