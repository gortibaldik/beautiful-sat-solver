import Vue from 'vue';
import Router from 'vue-router';
import Benchmarks from '@/components/Benchmarks'
import Results from '@/components/Results'
import BadGateway from '@/components/BadGateway'
import RedisLogs from '@/components/RedisLogs'
import CustomRun from '@/components/CustomRun'
import NQueens from '@/components/NQueens'
import NQueensResults from '@/components/NQueensResults'
import Sudoku from '@/components/Sudoku'


Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/benchmarks',
      name: 'Benchmarks',
      component: Benchmarks,
      props: { page: 1 },
      alias: '/'
    },
    {
      path: '/results',
      name: 'Results',
      component: Results,
      props: { page: 2 }
    },
    {
      path: '/redis_logs',
      name: 'Redis Logs',
      component: RedisLogs,
      props: { page: 3 }
    },
    {
      path: '/custom_run',
      name: 'Custom Run',
      props: { page: 4 },
      component: CustomRun
    },
    {
      path: '/nqueens',
      name: 'NQueens',
      props: { page: 5 },
      component: NQueens
    },
    {
      path: '/nqueens_results',
      name: 'NQueensResults',
      props: { page: 6 },
      component: NQueensResults
    },
    {
      path: '/sudoku',
      name: 'Sudoku',
      props: { page: 7 },
      component: Sudoku
    },
    {
      path: '/404',
      name: 'BadGateway',
      props: { page: 8 },
      component: BadGateway
    },
    {
      path: '*',
      props: { page: 8 },
      redirect: '/404'
    }
  ]
})