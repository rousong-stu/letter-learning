const viewGenerator = require('plop-templates/view/prompt')
const curdGenerator = require('plop-templates/curd/prompt')
const componentGenerator = require('plop-templates/component/prompt')

module.exports = (plop) => {
    plop.setGenerator('view', viewGenerator)
    plop.setGenerator('curd', curdGenerator)
    plop.setGenerator('component', componentGenerator)
}
