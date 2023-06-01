import { mutations, getters } from '@/store'

describe('mutations', () => {
  describe('SET_IMAGE_PATH', () => {
    it('should set the imagePath store prop to an_image', () => {
      // Given
      const state = { imagePath: null }
      const imagePath = 'an_image'
      // When
      mutations.SET_IMAGE_PATH(state, imagePath)
      // Then
      expect(state.imagePath).toBe(imagePath)
    })
  })
})

describe('getters', () => {
  describe('imagePath', () => {
    it('should return an_image', () => {
      // Given
      const imagePath = 'an_image'
      const state = { imagePath }
      // When
      const result = getters.imagePath(state)
      // Then
      expect(result).toBe(imagePath)
    })
  })
})
