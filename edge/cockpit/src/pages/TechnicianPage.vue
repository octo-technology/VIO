<template>
  <v-container fluid>
    <!-- LIST MODE -->
    <template v-if="mode === 'list'">
      <div class="d-flex align-center mb-4">
        <span class="text-h6">Configurations</span>
        <v-spacer />
        <v-btn prepend-icon="mdi-plus" variant="tonal" @click="newConfigDialog = true">New config</v-btn>
      </div>

      <v-row v-if="configs.length">
        <v-col v-for="cfg in configs" :key="cfg.station_name" cols="12" sm="6" md="4">
          <ConfigCard
            :config="cfg"
            :active-config-name="activeConfigName"
            :activating="activating"
            @edit="startEdit"
            @activate="activateConfig"
            @delete="confirmDelete"
          />
        </v-col>
      </v-row>

      <v-empty-state
        v-else
        icon="mdi-cog-outline"
        title="No configurations yet"
        subtitle="Create a new configuration to get started."
      />
    </template>

    <!-- EDIT MODE -->
    <template v-else>
      <v-card>
        <v-card-title class="d-flex align-center gap-2 pa-4">
          <v-btn icon="mdi-arrow-left" variant="text" size="small" @click="closeDraft" />
          <v-text-field
            ref="nameField"
            v-model="draft.station_name"
            :rules="[rules.required, uniqueEditableName]"
            density="compact"
            variant="plain"
            hide-details="auto"
            style="max-width:320px; font-size:1.1rem; font-weight:500"
          />
          <v-chip v-if="draft?.station_name === activeConfigName" size="x-small" color="primary" label>ACTIVE</v-chip>
          <v-spacer />
          <v-btn variant="plain" size="small" prepend-icon="mdi-restore" :disabled="isNewConfig" @click="resetDraft">Reset</v-btn>
        </v-card-title>
        <v-divider />

        <v-card-text>
          <v-form ref="form">
            <CamerasTable
              :camera-configs="draft.camera_configs"
              :camera-service-urls="cameraServiceUrls"
              :cameras-for-url="camerasForUrl"
              :camera-backend-for-url="cameraBackendForUrl"
              :rules="rules"
              :unique-camera-id="uniqueCameraId"
              @rename-camera="renameCameraId"
              @remove-camera="removeCamera"
              @add-camera="addCamera"
            />
            <PipelineStepsTable
              :pipeline-steps="draft.pipeline_steps"
              :camera-configs="draft.camera_configs"
              :model-server-urls="modelServerUrls"
              :models-for-url="modelsForUrl"
              :class-names-for-step="classNamesForStep"
              :camera-rule-items-for-step="cameraRuleItemsForStep"
              :rules="rules"
              :unique-step-id="uniqueStepId"
              @rename-step="renameStepId"
              @remove-step="removeStep"
              @add-step="addStep"
              @serving-url-change="onServingUrlChange"
              @model-name-change="onModelNameChange"
              @camera-rule-type-change="setCameraRuleType"
            />
            <ItemRuleEditor
              v-model:item-rule-config="draft.item_rule_config"
              :item-rule-type-items="itemRuleTypeItems"
              :rules="rules"
              @set-item-rule-type="setItemRuleType"
            />
            <StorageEditor
              v-model:binary-storage-config="draft.binary_storage_config"
              v-model:metadata-storage-config="draft.metadata_storage_config"
              :storage-type-items="storageTypeItems"
              :rules="rules"
              @storage-type-change="onStorageTypeChange"
            />
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-4" style="position:sticky; bottom:0; background:rgb(var(--v-theme-surface)); border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));">
          <v-spacer />
          <v-btn
            color="primary"
            :variant="isDirty ? 'flat' : 'tonal'"
            :disabled="!isDirty"
            prepend-icon="mdi-check"
            :loading="saving"
            @click="saveConfig"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </template>

    <!-- Delete config confirmation -->
    <v-dialog v-model="deleteConfigDialog" max-width="380">
      <v-card>
        <v-card-title>Supprimer la configuration ?</v-card-title>
        <v-card-text>
          Êtes-vous sûr de vouloir supprimer la configuration <strong>{{ configToDelete?.station_name }}</strong> ? Cette action est irréversible.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteConfigDialog = false">Cancel</v-btn>
          <v-btn color="error" :loading="deleting" @click="deleteConfig">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New config dialog -->
    <v-dialog v-model="newConfigDialog" max-width="420" @keydown.enter="newConfigNameForm?.validate().then(({ valid }) => valid && createNewConfig())">
      <v-card>
        <v-card-title>New configuration</v-card-title>
        <v-card-text>
          <v-form ref="newConfigNameForm">
            <v-text-field
              v-model="newConfigName"
              label="Config name"
              density="compact"
              variant="outlined"
              autofocus
              :rules="[rules.required, uniqueNewConfigName]"
              validate-on="input"
              hide-details="auto"
            />
            <div class="text-caption text-medium-emphasis mt-2">
              A blank config will be created — fill in the details and save.
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="newConfigDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="newConfigNameForm.validate().then(({ valid }) => valid && createNewConfig())">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="3000" location="bottom right">
      {{ snack.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useHealthStore } from '../features/system-health/stores/healthStore'
import { useConfigs } from '../features/station-config/composables/useConfigs'
import { useDiscovery } from '../features/station-config/composables/useDiscovery'
import { useConfigEditor } from '../features/station-config/composables/useConfigEditor'
import ConfigCard from '../features/station-config/components/ConfigCard.vue'
import CamerasTable from '../features/station-config/components/CamerasTable.vue'
import PipelineStepsTable from '../features/station-config/components/PipelineStepsTable.vue'
import ItemRuleEditor from '../features/station-config/components/ItemRuleEditor.vue'
import StorageEditor from '../features/station-config/components/StorageEditor.vue'

const { activeConfigName } = storeToRefs(useHealthStore())

const { configs, invalidate: invalidateConfigs } = useConfigs()

const {
  configOptions,
  cameraServiceUrls,
  modelServerUrls,
  camerasForUrl,
  cameraBackendForUrl,
  modelsForUrl,
} = useDiscovery()

const {
  mode, draft, originalConfig, isNewConfig,
  activating, saving, deleting, snack,
  form, nameField, newConfigDialog, newConfigName, newConfigNameForm,
  deleteConfigDialog, configToDelete,
  isDirty, itemRuleTypeItems, storageTypeItems,
  rules, uniqueCameraId, uniqueStepId, uniqueNewConfigName, uniqueEditableName,
  startEdit, closeDraft, resetDraft,
  activateConfig, confirmDelete, deleteConfig,
  createNewConfig, saveConfig,
  onStorageTypeChange, setCameraRuleType, setItemRuleType,
  addStep, removeStep, renameStepId,
  addCamera, removeCamera, renameCameraId,
  classNamesForStep, onModelNameChange, onServingUrlChange, cameraRuleItemsForStep,
} = useConfigEditor({ configs, invalidateConfigs, cameraServiceUrls, modelServerUrls, configOptions })

</script>
