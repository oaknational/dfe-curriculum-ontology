/**
 * Sanity Schema: Phase
 * Maps to: curric:Phase
 *
 * A phase of study in the education system (e.g., Primary, Secondary).
 */

export default {
  name: 'phase',
  title: 'Phase',
  type: 'document',
  icon: () => '🎓',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "primary", "secondary")',
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
      description: 'Display name for the phase',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Brief description of the phase',
      validation: Rule => Rule.required()
    },
    {
      name: 'lowerAgeBoundary',
      title: 'Lower Age Boundary',
      type: 'number',
      description: 'Minimum age for this phase',
      validation: Rule => Rule.required().min(0).integer()
    },
    {
      name: 'upperAgeBoundary',
      title: 'Upper Age Boundary',
      type: 'number',
      description: 'Maximum age for this phase',
      validation: Rule => Rule.required().positive().integer()
    }
  ],
  preview: {
    select: {
      title: 'label',
      subtitle: 'description',
      lowerAge: 'lowerAgeBoundary',
      upperAge: 'upperAgeBoundary'
    },
    prepare({title, subtitle, lowerAge, upperAge}) {
      return {
        title,
        subtitle: `Ages ${lowerAge}-${upperAge}: ${subtitle}`
      }
    }
  }
}
