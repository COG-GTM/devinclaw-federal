# cobol-conversion

## Overview
Convert COBOL programs to modern languages (Java, Python, TypeScript) while preserving business logic fidelity. Use this skill when modernizing enterprise ainframe COBOL applications in enterprise systems, when decommissioning mainframe infrastructure, or when business logic locked in COBOL must be made accessible to modern application architectures.

## When to Use
This skill converts COBOL programs -- including their copybooks, data divisions, procedure divisions, and inter-program communication patterns -- into modern languages while maintaining exact business logic equivalence. The conversion process is paragraph-by-paragraph, ensuring traceability between source COBOL and target code. It handles COBOL-specific constructs like packed decimal (COMP-3) arithmetic, REDEFINES clauses, OCCURS DEPENDING ON, PERFORM/GOTO flow control, and COPY/REPLACE preprocessor directives.

The the enterprise's mission-critical systems  and supporting administrative systems contain COBOL programs that have been in production for 30-40 years. These programs encode critical business rules for operations management, personnel systems, financial processing, and regulatory compliance. The COBOL developer workforce is aging out, making modernization urgent.

## Instructions
1. **Parse COBOL copybooks and data divisions**
   - Extract all COPY statements and resolve copybook inclusions (handle nested COPY and REPLACE directives).
   - Parse the IDENTIFICATION DIVISION for program metadata.
   - Parse the ENVIRONMENT DIVISION for FILE-CONTROL entries, SPECIAL-NAMES, and REPOSITORY paragraphs.
   - Parse the DATA DIVISION completely:
     - FILE SECTION: FD and SD entries with record layouts.
     - WORKING-STORAGE SECTION: All variable declarations.
     - LOCAL-STORAGE SECTION: Thread-local variables.
     - LINKAGE SECTION: Parameter definitions for inter-program communication.
   - Record every data item with its level number, PIC clause, USAGE clause, VALUE clause, REDEFINES, and OCCURS.

2. **Map data structures to target language**
   - Convert COBOL PIC clauses to target language types:
     - PIC X(n) to String (padded/trimmed as appropriate).
     - PIC 9(n) to int/long/Integer/BigInteger based on digit count.
     - PIC 9(n)V9(m) to BigDecimal (Java), Decimal (Python), or a decimal library (TypeScript).
     - PIC S9(n) COMP to int/long (binary).
     - PIC S9(n) COMP-3 to BigDecimal with packed decimal handling.
     - PIC S9(n)V9(m) COMP-3 to BigDecimal with appropriate scale.
   - Convert COBOL group items (levels 01-49) to classes/records/dataclasses in the target language.
   - Handle REDEFINES as union types or overlay accessors with explicit conversion methods.
   - Handle OCCURS (arrays) including OCCURS DEPENDING ON (variable-length arrays).
   - Handle 88-level condition names as named constants or enum values with validation methods.
   - Preserve FILLER fields in the data layout for binary compatibility during transition.

3. **Analyze PERFORM/GOTO control flow**
   - Map every PARAGRAPH and SECTION in the PROCEDURE DIVISION.
   - Trace all PERFORM statements (PERFORM, PERFORM THRU, PERFORM VARYING, PERFORM UNTIL, PERFORM TIMES).
   - Identify and catalog all GO TO statements and their targets.
   - Build a control flow graph.
   - Classify flow patterns:
     - Simple PERFORM to paragraph: Convert to method call.
     - PERFORM THRU range: Convert to sequential method calls or a single method encompassing the range.
     - PERFORM VARYING: Convert to for/while loops.
     - GO TO with single target: Convert to method call or restructure.
     - ALTER/GO TO (dynamic dispatch): Convert to strategy pattern or function pointer table.
   - Identify and restructure spaghetti code patterns (e.g., GO TO that jumps backward) into structured loops.

4. **Generate SDD specification**
   - For each COBOL program, produce an SDD that documents:
     - Program purpose and business context.
     - Input/output file descriptions and record layouts.
     - Database access patterns (if applicable).
     - Business rules extracted from procedure division logic.
     - Inter-program communication (CALL parameters and return codes).
     - Target language class/module structure.
     - Mapping table: COBOL paragraph to target method.
     - Mapping table: COBOL data item to target field/variable.

5. **Generate TDD test cases**
   - Create test cases that validate:
     - Data structure conversion correctness (byte-level accuracy for packed decimal, zoned decimal, and binary fields).
     - Arithmetic precision (COBOL's fixed-point arithmetic behavior must be exactly replicated).
     - String handling (COBOL right-pads with spaces; replicate this behavior).
     - Conditional logic (every IF/EVALUATE branch).
     - Loop behavior (PERFORM VARYING iteration counts).
     - File I/O equivalence (read/write same records in same order).
     - Inter-program call parameter passing.
     - Error handling and RETURN-CODE values.
   - If test data is available, create comparison tests that run both COBOL and target implementations against the same input.

6. **Convert paragraph by paragraph**
   - Convert each COBOL paragraph to a method in the target language, maintaining the paragraph name as the method name (converted to camelCase or snake_case as appropriate).
   - Convert COBOL verbs:
     - MOVE to assignment.
     - ADD/SUBTRACT/MULTIPLY/DIVIDE to arithmetic (preserving ON SIZE ERROR handling).
     - COMPUTE to expression evaluation.
     - IF/EVALUATE to if/switch.
     - STRING/UNSTRING to string concatenation/splitting.
     - INSPECT/TALLYING/REPLACING to string inspection/regex.
     - READ/WRITE/REWRITE/DELETE to file or database operations.
     - CALL to method invocation with parameter mapping.
     - ACCEPT/DISPLAY to I/O operations.
     - SORT/MERGE to collection sorting.
     - SEARCH/SEARCH ALL to linear/binary search.
   - Preserve COBOL's decimal arithmetic semantics -- never use floating-point for COMP-3 or numeric edited fields.
   - Handle CORRESPONDING (MOVE CORRESPONDING, ADD CORRESPONDING) by generating field-by-field operations.

7. **Handle COMP-3 and packed decimal**
   - Implement a packed decimal utility class/module that:
     - Converts packed decimal bytes to numeric values.
     - Converts numeric values back to packed decimal bytes.
     - Performs arithmetic with exact COBOL truncation and rounding semantics.
     - Handles sign nibble correctly (C=positive, D=negative, F=unsigned).
   - Ensure that all arithmetic operations on converted COMP-3 fields produce identical results to COBOL, including truncation behavior on overflow.
   - Create dedicated test cases that validate packed decimal handling with edge cases (max value, min value, zero, negative zero).

8. **Validate with comparison testing**
   - Run the original COBOL program and the converted program against identical test inputs.
   - Compare outputs byte-by-byte for file outputs and value-by-value for database operations.
   - Log any discrepancies with the specific paragraph, data item, and input that caused the difference.
   - Iterate on the conversion until all comparison tests pass with zero discrepancies.
   - For programs that cannot be run on-premise (mainframe-only), use recorded test output as the comparison baseline.

9. **Create pull requests**
   - Create a PR for each converted program with:
     - Converted source code.
     - All test cases.
     - SDD specification.
     - Comparison test results.
     - COBOL-to-target mapping table for audit traceability.
   - Invoke Devin Review on the PR.
   - Include the original COBOL source in the PR as a reference (in a `legacy/` directory).

## Specifications
- **Arithmetic precision**: All numeric conversions must use fixed-point decimal arithmetic (BigDecimal in Java, Decimal in Python). Floating-point (float, double) is prohibited for business calculations.
- **COMP-3 fidelity**: Packed decimal conversion must be bit-accurate. A utility class must be provided and unit-tested independently.
- **String handling**: COBOL strings are fixed-length and space-padded. The target implementation must preserve this behavior where it affects business logic. Provide utility methods for COBOL-style string comparison (trailing spaces ignored).
- **RETURN-CODE**: COBOL's RETURN-CODE special register must be mapped to an explicit return value or exit code in the target language.
- **File I/O**: Sequential file reads (READ ... AT END) must map to iterator patterns. VSAM KSDS access must map to key-value store or database table access.
- **EBCDIC/ASCII**: If the source COBOL runs on z/OS (EBCDIC), character encoding conversion must be handled. All target code operates in UTF-8.
- **Copybook reuse**: Shared copybooks must be converted to shared libraries/modules in the target language, not duplicated per program.
- **Naming**: COBOL names with hyphens (e.g., WS-CUSTOMER-NAME) convert to camelCase (Java/TypeScript) or snake_case (Python): wsCustomerName or ws_customer_name.
- **Traceability**: Every converted method must include a comment referencing the original COBOL paragraph name and line number range.
- **Line-for-line mapping**: Maintain a machine-readable mapping file (JSON) linking every COBOL paragraph to its target language method for audit purposes.

## Advice
- COBOL copybooks are shared across programs. Convert them first and create a shared library, then convert individual programs that reference them.
- Pay special attention to COBOL's COMPUTE statement with complex expressions. COBOL evaluates left to right with intermediate rounding at each step, which differs from standard mathematical operator precedence in modern languages. Use explicit parentheses and intermediate variables to match COBOL behavior.
- REDEFINES is COBOL's version of a union type. The most reliable conversion is a wrapper class that lazily interprets the same byte buffer in different ways.
- COBOL EVALUATE (ALSO) is more powerful than a simple switch statement. It can evaluate multiple conditions simultaneously. Map to nested if-else or pattern matching constructs.
- INSPECT TALLYING/REPLACING is the COBOL string processing workhorse. Map it carefully -- it has subtle behavior around BEFORE/AFTER INITIAL that does not map directly to regex.
- Many COBOL programs rely on the fact that WORKING-STORAGE is initialized once at program load and persists across calls (unlike LOCAL-STORAGE). In the target language, this maps to instance variables, not local variables.
- COBOL's SORT verb with INPUT PROCEDURE and OUTPUT PROCEDURE is essentially a coroutine pattern. In Java, implement with a custom Comparator and stream processing. In Python, use generators.
- When encountering ALTER ... TO PROCEED TO statements (self-modifying code), this is the COBOL equivalent of function pointers. Convert to a strategy pattern with explicit state management.

## Forbidden Actions
- Do not use floating-point types (float, double) for any numeric field that was COMP-3, COMP, or numeric edited in COBOL. This will introduce rounding errors that corrupt financial calculations.
- Do not silently drop FILLER fields during conversion. They may participate in REDEFINES overlays or have significance in file record layouts.
- Do not ignore COBOL's implicit decimal point behavior (V in PIC clause). Every V must be converted to explicit decimal handling.
- Do not convert GO TO statements to goto in Java (which does not exist as a usable statement) or unstructured jumps. Restructure the control flow.
- Do not assume COBOL performs arithmetic the same way as modern languages. COBOL truncates on overflow by default (unless ON SIZE ERROR is specified). Document and replicate this behavior.
- Do not merge or rename COBOL paragraphs during conversion. Maintain 1:1 traceability for audit compliance.
- Do not omit the comparison testing step. Business logic equivalence must be proven, not assumed.
- Do not convert EXEC SQL or EXEC CICS blocks without understanding the middleware context. These require separate handling through the plsql-migration or api-modernization skills.

---
*Generated by DevinClaw Skills Parser at 2026-02-25T06:27:28Z*
*Source: skills/cobol-conversion/SKILL.md*
