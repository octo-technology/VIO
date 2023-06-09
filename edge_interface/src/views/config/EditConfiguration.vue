<!-- <template>
  <div class="container">
    <h3>Form test</h3>

    <v-form v-model="valid">
      <v-jsf v-model="model" :schema="schema" :options="options">
        <template
          slot="custom-string"
          slot-scope="{ value, label, on }"
          v-if="value"
        >
          <p class="mt-4">
            {{ label }}
            <input
              type="text"
              :value="value"
              v-on="on"
              style="border:1px solid green;"
            />
          </p>
        </template>

        <template slot="custom-avatar" slot-scope="context">
          <v-jsf-crop-img v-bind="context" />
        </template>
        <template slot="custom-tabs1" slot-scope="context">
          <v-jsf-custom-tabs v-bind="context" />
        </template>

        <template slot="custom-tabs" slot-scope="{ value, schema }">
          <div v-if="value">
            <v-tabs>
              <v-tab v-for="cameraId in value" :key="cameraId.itemTitle">{{
                cameraId.name
              }}</v-tab>
              <v-btn
                color="primary"
                fab
                small
                absolute
                right
                @click="add_camera()"
                ><v-icon>mdi-plus</v-icon>
              </v-btn>
              <template v-for="(cameraId, index) in value">
                <v-tab-item :key="cameraId.itemTitle">
                  <v-jsf
                    v-model="value[index]"
                    :schema="schema.items"
                    :options="options"
                  ></v-jsf>
                </v-tab-item>
              </template>
            </v-tabs>
          </div>
        </template>
      </v-jsf>
    </v-form>
    <pre>
ORIGINAL
{{ JSON.stringify(model, null, 2) }}
    </pre>
    <pre>
CONVERTED
{{ JSON.stringify(converted, null, 2) }}
    </pre>
  </div>
</template>

<script>
import VJsf from "@koumoul/vjsf/lib/VJsf.js";
import ConfigService from "@/services/ConfigService";
import "@koumoul/vjsf/lib/VJsf.css";
import "@koumoul/vjsf/lib/deps/third-party.js";
import VJsfCropImg from "@/components/v-jsf-crop-img.vue";
import VJsfCustomTabs from "@/components/v-jsf-custom-tabs.vue";
import { schema } from "./schema";
// import _ from "lodash";

export default {
  name: "edit-configuration",
  components: { VJsf, VJsfCropImg, VJsfCustomTabs },
  props: {
    config_id: String,
  },
  data: () => ({
    valid: false,
    model: {},
    inventory: {},

    schema,
    options: {
      editMode: "inline",
    },
  }),
  computed: {
    converted: function() {
      // console.log("test", arrayToObject([1,2,3,4]))
      // return traverse(this.model);
      // return arrayToObject(this.model, 'id')
      return {}
    },
  },
  async created() {
    // Load inventory before the other API (to avoid key errors)
    await ConfigService.get_inventory().then((response) => {
      this.inventory = response.data;
      // console.log(this.inventory);
    });
  },

  methods: {
    add_camera: function() {
      this.model.ListOfCameras.push({ name: "new camera" });
    },
  },
};

// const arrayToObject = (arr, key = "id") => {
//   if (
//     _.every(
//       arr.map((obj) => (_.isObject(obj) ? key in obj : false ))
//     )
//   ) {
//     return arr.reduce((obj, item) => {
//       let item_copy = _.cloneDeep(item);
//       delete item_copy[key];
//       obj[item[key]] = item_copy;
//       return obj;
//     }, {});
//   } else {
//     return arr;
//   }
// };

// function convert(formToConfiguration) {
//   let result = {};

//   _.forIn(obj, function(val, key) {
    

//       val = arrayToObject(val);
//       console.log(val);
//       result[key] = val;
//     }
//     if (_.isObject(key)) {
//       result = traverse(result[key]);
//     }
//   });
//   return result;
// }
</script>

<style lang="scss" scoped></style> -->
