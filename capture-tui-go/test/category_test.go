package test

import (
	"testing"
	"time"

	"github.com/capture-tui/capture/internal/models"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestCategory(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Category Suite")
}

var _ = Describe("Category", func() {
	Describe("Creating a new category", func() {
		Context("with all fields", func() {
			It("should create category with correct values", func() {
				cat := models.NewCategory("features", "Feature Requests", "Ideas for new features")

				Expect(cat.Name).To(Equal("features"))
				Expect(cat.DisplayName).To(Equal("Feature Requests"))
				Expect(cat.Description).To(Equal("Ideas for new features"))
				Expect(cat.Count).To(Equal(0))
				Expect(cat.CreatedAt).To(BeTemporally("~", time.Now(), time.Second))
			})
		})

		Context("with empty display name", func() {
			It("should use name as display name", func() {
				cat := models.NewCategory("bugs", "", "Bug reports")
				cat.SetDisplayName("")

				Expect(cat.DisplayName).To(Equal("bugs"))
			})
		})
	})

	Describe("Updating entry count", func() {
		Context("adding entries", func() {
			It("should increase count and update last entry time", func() {
				cat := models.NewCategory("test", "Test", "")
				
				cat.UpdateCount(1)

				Expect(cat.Count).To(Equal(1))
				Expect(cat.LastEntry).NotTo(BeNil())
				Expect(*cat.LastEntry).To(BeTemporally("~", time.Now(), time.Second))
			})
		})

		Context("removing entries", func() {
			It("should decrease count", func() {
				cat := models.NewCategory("test", "Test", "")
				cat.UpdateCount(5)

				cat.UpdateCount(-1)

				Expect(cat.Count).To(Equal(4))
			})
		})

		Context("count goes below zero", func() {
			It("should clamp to zero", func() {
				cat := models.NewCategory("test", "Test", "")
				cat.UpdateCount(2)

				cat.UpdateCount(-5)

				Expect(cat.Count).To(Equal(0))
			})
		})
	})

	Describe("Setting display name", func() {
		Context("with valid display name", func() {
			It("should set the display name", func() {
				cat := models.NewCategory("feat", "", "")
				cat.SetDisplayName("Features & Improvements")

				Expect(cat.DisplayName).To(Equal("Features & Improvements"))
			})
		})

		Context("with empty display name", func() {
			It("should fallback to category name", func() {
				cat := models.NewCategory("archived", "Old Name", "")
				cat.SetDisplayName("")

				Expect(cat.DisplayName).To(Equal("archived"))
			})
		})
	})
})
