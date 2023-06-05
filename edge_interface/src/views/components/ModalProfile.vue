<template>
    <div class="full-height">
        <v-card>
            <v-toolbar dark color="secondary darken-1" dense>
                <v-btn icon dark @click.native="close()">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title>Choose parameters</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-toolbar-items>
                    <v-btn dark text @click.native="close()">Save</v-btn>
                </v-toolbar-items>
            </v-toolbar>

            <v-card-text class="full-height">

                <v-item-group active-class="primary" mandatory>
                    <v-container>
                        <v-row>
                            <v-col cols="12" md="3">
                                <v-card class="d-flex align-center transparent" height="100">
                                    <div class="text-h4 flex-grow-1 text-right">
                                        Location
                                    </div>
                                </v-card>

                            </v-col>
                            <v-col cols="12" md="4">
                                <!-- v-for="n in 3" :key="n" -->
                                <v-item v-slot:default="{ active, toggle }">
                                    <v-card class="d-flex align-center" dark height="100" @click="toggle">
                                        <!-- <div v-if="active" class="display-3 flex-grow-1 text-center">Active</div> -->
                                        <div class="text-h4 flex-grow-1 text-center">
                                            HAM
                                        </div>

                                    </v-card>
                                </v-item>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-item v-slot:default="{ active, toggle }">
                                    <v-card class="d-flex align-center" dark height="100" @click="toggle">
                                        <!-- <div v-if="active" class="display-3 flex-grow-1 text-center">Active</div> -->
                                        <div class="text-h4 flex-grow-1 text-center">
                                            TLS
                                        </div>

                                    </v-card>
                                </v-item>
                            </v-col>
                        </v-row>
                    </v-container>
                </v-item-group>

                <v-container>
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-card class="d-flex align-center transparent" height="100">
                                <div class="text-h4 flex-grow-1 text-right">
                                    Comments
                                </div>
                            </v-card>
                        </v-col>
                        <v-col cols="12" md="8">
                            <div class="text-h4 flex-grow-1 text-right">
                                <v-textarea clearable style="font-size: 1em;"></v-textarea>
                            </div>
                        </v-col>
                    </v-row>
                </v-container>

            </v-card-text>




        </v-card>
    </div>
</template>

<script>
export default {
    name: "App",
    props: {
        open: Boolean
    },
    methods: {
        close() {
            this.$emit("close", false);
        }
    }
}

</script>

<style scoped>
.full-height {
    height: 100vh;
    background-color: #000;
}
</style>