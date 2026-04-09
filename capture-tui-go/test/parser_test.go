package test

import (
	"testing"

	"github.com/capture-tui/capture/internal/parser"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestParser(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Parser Suite")
}

var _ = Describe("Extractors", func() {
	Describe("Task Extractor", func() {
		var extractor *parser.TaskExtractor

		BeforeEach(func() {
			extractor = parser.NewTaskExtractor()
		})

		Context("extracting markdown todos", func() {
			It("should extract tasks from markdown checkboxes", func() {
				content := "- [ ] Task 1\n- [ ] Task 2"
				tasks := extractor.Extract(content)

				Expect(tasks).To(ContainElements("Task 1", "Task 2"))
			})
		})

		Context("extracting TODO keywords", func() {
			It("should extract tasks from TODO: syntax", func() {
				content := "TODO: Implement authentication"
				tasks := extractor.Extract(content)

				Expect(tasks).To(ContainElement("Implement authentication"))
			})

			It("should extract tasks from Chinese 任务 syntax", func() {
				content := "任务: 完成设计文档"
				tasks := extractor.Extract(content)

				Expect(tasks).To(ContainElement("完成设计文档"))
			})
		})

		Context("deduplication", func() {
			It("should not duplicate identical tasks", func() {
				content := "- [ ] Same Task\n- [ ] Same Task"
				tasks := extractor.Extract(content)

				Expect(tasks).To(HaveLen(1))
			})
		})
	})

	Describe("Tag Extractor", func() {
		var extractor *parser.TagExtractor

		BeforeEach(func() {
			extractor = parser.NewTagExtractor()
		})

		Context("extracting hashtags", func() {
			It("should extract tags from #tag format", func() {
				content := "This is a #feature with #important tag"
				tags := extractor.Extract(content)

				Expect(tags).To(ContainElements("feature", "important"))
			})
		})

		Context("lowercase conversion", func() {
			It("should convert tags to lowercase", func() {
				content := "#FEATURE #Important"
				tags := extractor.Extract(content)

				Expect(tags).To(ContainElements("feature", "important"))
			})
		})

		Context("deduplication", func() {
			It("should not duplicate identical tags", func() {
				content := "#tag #tag #TAG"
				tags := extractor.Extract(content)

				Expect(tags).To(HaveLen(1))
				Expect(tags[0]).To(Equal("tag"))
			})
		})
	})

	Describe("Priority Extractor", func() {
		var extractor *parser.PriorityExtractor

		BeforeEach(func() {
			extractor = parser.NewPriorityExtractor()
		})

		Context("extracting P0 priority", func() {
			It("should detect P0 keyword", func() {
				content := "This is a P0 priority task"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P0"))
			})

			It("should detect urgent keyword", func() {
				content := "This is urgent"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P0"))
			})

			It("should detect Chinese urgent marker", func() {
				content := "【紧急】需要处理的问题"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P0"))
			})
		})

		Context("extracting P1 priority", func() {
			It("should detect P1 keyword", func() {
				content := "This is P1 priority"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P1"))
			})

			It("should detect important keyword", func() {
				content := "This is important"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P1"))
			})

			It("should detect Chinese important marker", func() {
				content := "【重要】待办事项"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P1"))
			})
		})

		Context("default priority", func() {
			It("should return P2 when no priority found", func() {
				content := "Just a normal task"
				priority := extractor.Extract(content)

				Expect(priority).To(Equal("P2"))
			})
		})
	})

	Describe("Title Extractor", func() {
		var extractor *parser.TitleExtractor

		BeforeEach(func() {
			extractor = parser.NewTitleExtractor()
		})

		Context("extracting from markdown heading", func() {
			It("should extract title from # heading", func() {
				content := "# My Title\n\nSome content"
				title := extractor.Extract(content)

				Expect(title).To(Equal("My Title"))
			})
		})

		Context("extracting from first line", func() {
			It("should use first non-empty line as title", func() {
				content := "First line of text\n\nMore content"
				title := extractor.Extract(content)

				Expect(title).To(Equal("First line of text"))
			})
		})

		Context("empty content", func() {
			It("should return Untitled for empty content", func() {
				title := extractor.Extract("")

				Expect(title).To(Equal("Untitled"))
			})
		})

		Context("long title", func() {
			It("should truncate long titles", func() {
				extractor.SetMaxLength(10)
				content := "This is a very long title that should be truncated"
				title := extractor.Extract(content)

				Expect(title).To(HaveLen(10))
			})
		})
	})
})
