# Drag and Drop — values repair

Teacher Question Bank > Edit > Drag and Drop Image now has a dedicated **Draggable Values** field. The original coordinate labels are `(-2,-1); (-2,1); (2,-1); (2,1)` (rendered with the labels you enter). You may also enter `1,1,1,1` to create four distinct draggable tokens with the same label.

Saving preserves existing choice IDs and quadrant answer mappings whenever present, rather than wiping `drag_config`. For questions whose choices were already erased by an earlier save, editing and saving will reconstruct four choices and a default quadrant mapping. Review the answer mapping for customized old questions.

No migration is needed. This is based on the Render-fix project, not the later rebuilt drag-and-drop branch.
