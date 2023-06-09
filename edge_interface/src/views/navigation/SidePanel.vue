<template>
    <v-navigation-drawer app permanent>
        <v-list>
            <v-list-item>
                <v-list-item-content>
                    <v-list-item-title class="text-h6">Menu</v-list-item-title>
                    <v-list-item-subtitle> </v-list-item-subtitle>
                </v-list-item-content>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item link to="/camera">
                <v-list-item-action><v-icon>mdi-camera</v-icon></v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>Camera</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item link to="/item-list">
                <v-list-item-action><v-icon>mdi-cog</v-icon></v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>Item List</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item link to="/item-gallery">
                <v-list-item-action><v-icon>mdi-view-module</v-icon></v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>Item Gallery</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item link to="/upload-files">
                <v-list-item-action>
                    <v-icon>mdi-cloud-upload</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>Upload</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <!-- <v-list-item link to="/upload-camera">
                <v-list-item-action>
                    <v-icon>mdi-camera</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>
                        Camera
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item> -->
            <!-- <v-list-item link to="/trigger">
                <v-list-item-action>
                    <v-icon>mdi-cloud-upload</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>
                        Trigger
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item> -->
            <v-list-item link to="/config">
                <v-list-item-action>
                    <v-icon>mdi-cog</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>
                        Config
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item link to="/about">
                <v-list-item-action>
                    <v-icon>mdi-view-dashboard</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>
                        About
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

