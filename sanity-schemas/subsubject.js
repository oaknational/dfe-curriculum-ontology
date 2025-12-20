/**
 * Sanity Schema: Sub-Subject
 * Maps to: curric:SubSubject
 * Properties: rdfs:label, rdfs:comment
 *
 * A sub-subject within a subject (e.g., Biology within Science).
 */

export default {
  name: 'subsubject',
  title: 'Sub-Subject',
  type: 'document',
  icon: () => '📗',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "subsubject-science")',
      validation: Rule => Rule.required(),
      options: {
        source: 'label',
        maxLength: 100,
      }
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Sub-subject name (maps to rdfs:label)',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Brief description (maps to rdfs:comment)',
      validation: Rule => Rule.required()
    },
    {
      name: 'fullDescription',
      title: 'Full Description',
      type: 'text',
      description: 'Detailed description from curriculum documents (maps to dcterms:description)',
      rows: 5
    },
    {
      name: 'subject',
      title: 'Parent Subject',
      type: 'reference',
      description: 'The subject this sub-subject belongs to',
      to: [{type: 'subject'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'strands',
      title: 'Strands',
      type: 'array',
      description: 'Knowledge strands included in this sub-subject',
      of: [{type: 'reference', to: [{type: 'strand'}]}]
    },
    {
      name: 'aims',
      title: 'Educational Aims',
      type: 'array',
      description: 'Specific aims for this sub-subject (maps to curric:hasAim)',
      of: [{
        type: 'object',
        fields: [
          {
            name: 'aimText',
            title: 'Aim',
            type: 'text',
            validation: Rule => Rule.required()
          }
        ],
        preview: {
          select: {
            title: 'aimText'
          },
          prepare({title}) {
            return {
              title: title?.substring(0, 60) + (title?.length > 60 ? '...' : '')
            }
          }
        }
      }]
    },
    {
      name: 'sourceUrl',
      title: 'Source URL',
      type: 'url',
      description: 'Link to official curriculum documentation (maps to dcterms:source)'
    }
  ],
  preview: {
    select: {
      title: 'label',
      subtitle: 'description',
      subject: 'subject.label'
    },
    prepare({title, subtitle, subject}) {
      return {
        title,
        subtitle: `${subject} - ${subtitle}`
      }
    }
  }
}
