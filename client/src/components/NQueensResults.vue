<template>
  <results-prototype
    title="Results of Past Runs of NQueens Problem"
    barChartSecondLabel="Number of Queens"
    serverSubpath="/nqueens_results/"
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