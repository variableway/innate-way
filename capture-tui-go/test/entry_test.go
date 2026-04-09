package test

import (
	"strings"
	"testing"
	"time"

	"github.com/capture-tui/capture/internal/models"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestEntry(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Entry Suite")
}

var _ = Describe("Entry", func() {
	Describe("Creating a new entry", func() {
		Context("with basic information", func() {
			It("should create an entry with generated ID", func() {
				entry := models.NewEntry("Test Title", "Test Content", "test-category", []string{"tag1", "tag2"})

				Expect(entry.Title).To(Equal("Test Title"))
				Expect(entry.Content).To(Equal("Test Content"))
				Expect(entry.Category).To(Equal("test-category"))
				Expect(entry.Tags).To(Equal([]string{"tag1", "tag2"}))
				Expect(entry.ID).To(HavePrefix("ideas-"))
				Expect(entry.CreatedAt).To(BeTemporally("~", time.Now(), time.Second))
			})

			It("should have default metadata", func() {
				entry := models.NewEntry("Test", "Content", "test", []string{})

				Expect(entry.Metadata.Source).To(Equal("cli"))
				Expect(entry.Metadata.Priority).To(Equal("P2"))
			})
		})
	})

	Describe("Converting to Markdown", func() {
		Context("with all fields populated", func() {
			It("should generate valid Markdown with frontmatter", func() {
				entry := models.NewEntry("Test Title", "Test Content", "features", []string{"ui", "important"})
				entry.Tasks = []string{"Task 1", "Task 2"}
				entry.Metadata.Priority = "P1"

				md := entry.ToMarkdown()

				Expect(md).To(ContainSubstring("---"))
				Expect(md).To(ContainSubstring("id: \"" + entry.ID + "\""))
				Expect(md).To(ContainSubstring("category: \"features\""))
				Expect(md).To(ContainSubstring("priority: \"P1\""))
				Expect(md).To(ContainSubstring("# Test Title"))
				Expect(md).To(ContainSubstring("Test Content"))
				Expect(md).To(ContainSubstring("## 关联任务"))
				Expect(md).To(ContainSubstring("- [ ] Task 1"))
				Expect(md).To(ContainSubstring("- [ ] Task 2"))
			})
		})

		Context("without tasks", func() {
			It("should not include task section", func() {
				entry := models.NewEntry("Test", "Content", "test", []string{})
				md := entry.ToMarkdown()

				Expect(md).NotTo(ContainSubstring("## 关联任务"))
			})
		})
	})

	Describe("Parsing from Markdown", func() {
		Context("with valid markdown", func() {
			It("should parse entry correctly", func() {
				md := `---
id: "ideas-20240115-001"
category: "features"
created_at: "2024-01-15T10:30:00+08:00"
tags: ["ui", "performance"]
priority: "P1"
source: "cli"
---

# Test Title

This is the content.

## 关联任务

- [ ] Task 1
- [ ] Task 2
`
				entry, err := models.EntryFromMarkdown(md)

				Expect(err).To(BeNil())
				Expect(entry.ID).To(Equal("ideas-20240115-001"))
				Expect(entry.Title).To(Equal("Test Title"))
				Expect(entry.Category).To(Equal("features"))
				Expect(entry.Tags).To(ContainElements("ui", "performance"))
				Expect(entry.Metadata.Priority).To(Equal("P1"))
				Expect(entry.Tasks).To(HaveLen(2))
				Expect(entry.Tasks).To(ContainElements("Task 1", "Task 2"))
			})
		})

		Context("with missing frontmatter", func() {
			It("should return an error", func() {
				md := "# Just a title\n\nSome content"
				_, err := models.EntryFromMarkdown(md)

				Expect(err).To(HaveOccurred())
				Expect(err.Error()).To(ContainSubstring("frontmatter"))
			})
		})

		Context("with empty content", func() {
			It("should return an error", func() {
				_, err := models.EntryFromMarkdown("")

				Expect(err).To(HaveOccurred())
			})
		})
	})

	Describe("Task management", func() {
		Context("adding tasks", func() {
			It("should add tasks to entry", func() {
				entry := models.NewEntry("Test", "Content", "test", []string{})
				entry.AddTask("New Task")

				Expect(entry.Tasks).To(ContainElement("New Task"))
				Expect(entry.TaskCount()).To(Equal(1))
				Expect(entry.HasTasks()).To(BeTrue())
			})
		})

		Context("with no tasks", func() {
			It("should report no tasks", func() {
				entry := models.NewEntry("Test", "Content", "test", []string{})

				Expect(entry.HasTasks()).To(BeFalse())
				Expect(entry.TaskCount()).To(Equal(0))
			})
		})
	})

	Describe("Round-trip conversion", func() {
		It("should preserve entry after to and from markdown", func() {
			original := models.NewEntry("Original Title", "Original content here.", "test-cat", []string{"tag1"})
			original.Tasks = []string{"Task A", "Task B"}
			original.Metadata.Priority = "P0"

			md := original.ToMarkdown()
			restored, err := models.EntryFromMarkdown(md)

			Expect(err).To(BeNil())
			Expect(restored.Title).To(Equal(original.Title))
			Expect(restored.Category).To(Equal(original.Category))
			Expect(restored.Metadata.Priority).To(Equal(original.Metadata.Priority))
			Expect(restored.Tasks).To(Equal(original.Tasks))
		})
	})
})
