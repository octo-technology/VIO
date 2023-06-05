<template>
    <v-col class="container">
        <div v-for="(camera, index) in predictedItems" :key="index">
            <ImageWithBoxes :camera="camera"></ImageWithBoxes>
        </div>

        <v-fab-transition>
            <v-btn color="blue darken-3" dark absolute bottom right fab style="bottom: 16px" @click="goToSimpleCamera">
                <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
        </v-fab-transition>
    </v-col>
</template>

<script>
import ItemsService from "@/services/ItemsService";
import ImageWithBoxes from "./components/ImageWithBoxes.vue";
import { baseURL } from "@/services/api";

export default {
    // props: ["itemId"],
    data: () => ({
        state: undefined,
        decision: undefined,
        predictedItems: [],
        statusList: {
            "Capture": 0,
            "Save Binaries": 1,
            "Inference": 2,
            "Decision": 3,
            "Done": 4,
        },

    }),
    components: {
        ImageWithBoxes
    },
    async beforeMount() {
        this.itemId = this.$route.params.itemId

        await this.fetchItem();

        if(this.state != "Done") {
            console.log("fetching polling")
            await this.waitForStateDone();
            await this.fetchItem();
        }

    },
    methods: {
        goToSimpleCamera() {
            this.$router.push({ name: "Simple-Camera" });
        },
        async fetchItem() {
            let itemResponse = await ItemsService.get_item_by_id(this.itemId)
            const item = itemResponse.data;
            this.state = item["state"];
            this.decision = item["decision"];
            const inferences = item["inferences"];

            Object.keys(inferences).forEach((camera_id) => {
                this.predictedItems.push({
                    camera_id: camera_id,
                    inferences: inferences[camera_id],
                    image_url: `${baseURL}/items/${this.itemId}/binaries/${camera_id}`,
                });
            });
            // console.log("inferences", inferences)
            // console.log("predicted", this.predictedItems)

        },
        async waitForStateDone() {
            const maxAttempts = 20;
            let attempts = 0;
            const executePoll = async (resolve, reject) => {
                const result = await ItemsService.get_item_state_by_id(this.itemId);
                this.state = result.data;

                console.log("STATE POLLING", this.state);
                attempts++;

                if (this.state === "Done") {
                    return resolve(result);
                } else if (attempts === maxAttempts) {
                    return reject(new Error("L'inférence n'a pas pu être réalisée"));
                } else {
                    setTimeout(executePoll, 800, resolve, reject);
                }
            };
            return new Promise(executePoll);
        },
    }
}
</script>

<style lang="scss" scoped>
.container {
    text-align: center;
    // height: 100vh;
    margin: 0;
    padding: 0;

}
</style>