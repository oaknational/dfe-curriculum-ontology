/**
 * Sanity Schema: Subject
 * Maps to: curric:Subject
 * Properties: rdfs:label, rdfs:comment
 *
 * A subject in the curriculum (e.g., Science, History, Mathematics).
 */

export default {
  name: 'subject',
  title: 'Subject',
  type: 'document',
  icon: () => '📖',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "subject-science")',
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
      description: 'Subject name (maps to rdfs:label)',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Brief description of the subject (maps to rdfs:comment)',
      validation: Rule => Rule.required()
    },
    {
      name: 'disciplines',
      title: 'Disciplines',
      type: 'array',
      description: 'Disciplines that this subject draws from',
      of: [{type: 'reference', to: [{type: 'discipline'}]}],
      validation: Rule => Rule.required().min(1)
    }
  ],
  preview: {
    select: {
      title: 'label',
      subtitle: 'description'
    }
  }
}
