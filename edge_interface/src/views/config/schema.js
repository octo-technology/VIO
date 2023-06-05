export let schema = {
    type: "object",
    properties: {
        id: {
            type: "string",
            title: "Configuration id",
            description: "The id of the configuration",
        },
        // avatarProp: {
        //     type: "string",
        //     title: `I'm a base64 png image string`,
        //     "x-display": "custom-avatar",
        // },

        cameras: {
            type: "array",
            title: "List of cameras",
            "x-options": { arrayItemCardProps: { outlined: false } },
            default: [{
                id: "camera front",
                type: "pi_camera",
            }],
            // "x-display": "custom-tabs",
            "x-itemTitle": "id",
            items: {
                $ref: "#/definitions/camera",
            },
        },
    },
    definitions: {
        camera: {
            type: "object",
            "x-itemTitle": "name",
            required: ["id"],
            properties: {
                id: {
                    type: "string",
                },
                type: {
                    type: "string",
                    title: "Camera type",
                    enum: ["fake", "pi_camera", "usb_camera"],
                    default: "pi_camera",
                    "x-cols": 6,
                },
                input_images_folder: {
                    type: "string",
                    "x-cols": 6,
                },
                position: {
                    type: "string",
                    "x-cols": 6,
                },
                exposition: {
                    type: "number",
                    "x-cols": 6,
                },

                models_graph: { $ref: "#/definitions/modelsArray" },
            },
        },
        modelsArray: {
            type: "array",
            title: "Models",
            "x-options": { arrayItemCardProps: { outlined: false } },
            "x-itemTitle": "id",
            items: {
                type: "object",
                required: ["id"],
                properties: {
                    id: {
                        type: "string",
                        title: "Model name",
                        default: "Model",
                    },
                    metadata: {
                        type: "string",
                    },
                    depends_on: {
                        type: "array",
                        "x-cols": 6,
                        "items": {
                            "type": "string"
                        }
                    },
                    class_to_detect: {
                        type: "array",
                        "x-cols": 6,
                        "items": {
                            "type": "string"
                        }
                    },
                },
            },
        },
    },
};