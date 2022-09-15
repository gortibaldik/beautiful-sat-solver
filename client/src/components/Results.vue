<template>
  <results-prototype
    title="Results of Past Benchmark Runs"
    barChartSecondLabel="Benchmark"
    serverSubpath="/results/"
  />
</template>
<script>
import ResultsPrototype from '@/components/ResultsPrototype.vue'

export default {
  components: {
    ResultsPrototype
  },
  data() {
    return {}
  }
}
</script>