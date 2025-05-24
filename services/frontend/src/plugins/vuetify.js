import {createVuetify} from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        themes: {
            light: {
                colors: {
                    primary: '#1976D2',
                    secondary: '#424242',
                    accent: '#82B1FF',
                    error: '#FF5252',
                    info: '#2196F3',
                    success: '#4CAF50',
                    warning: '#FFC107',
                    lightgrey: '#d3d0d0'
                }
            },
            dark: {
                colors: {
                    primary: '#90CAF9',
                    secondary: '#616161',
                    accent: '#B39DDB',
                    error: '#EF5350',
                    info: '#64B5F6',
                    success: '#81C784',
                    warning: '#FFD54F',
                    lightgrey: '#404040'
                }
            }
        }
    }
})