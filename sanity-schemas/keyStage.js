/**
 * Sanity Schema: Key Stage
 * Maps to: curric:KeyStage
 *
 * A key stage that structures learning for specific age groups.
 */

export default {
  name: 'keyStage',
  title: 'Key Stage',
  type: 'document',
  icon: () => '📚',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "key-stage-1", "key-stage-2")',
      validation: Rule => Rule.required(),
      options: {
        source: 'label',
        maxLength: 50,
      }
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Display name (e.g., "Key Stage 1")',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Brief description of the key stage',
      validation: Rule => Rule.required()
    },
    {
      name: 'phase',
      title: 'Phase',
      type: 'reference',
      description: 'The phase this key stage belongs to',
      to: [{type: 'phase'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'lowerAgeBoundary',
      title: 'Lower Age Boundary',
      type: 'number',
      description: 'Minimum age for this key stage',
      validation: Rule => Rule.required().min(0).integer()
    },
    {
      name: 'upperAgeBoundary',
      title: 'Upper Age Boundary',
      type: 'number',
      description: 'Maximum age for this key stage',
      validation: Rule => Rule.required().positive().integer()
    }
  ],
  preview: {
    select: {
      title: 'label',
      subtitle: 'description',
      phase: 'phase.label'
    },
    prepare({title, subtitle, phase}) {
      return {
        title,
        subtitle: `${phase} - ${subtitle}`
      }
    }
  }
}
