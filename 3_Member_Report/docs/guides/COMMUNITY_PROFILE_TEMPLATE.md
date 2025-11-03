# Community Profile Data Extraction Template

Use this template when extracting data from Community Profile PDFs to ensure consistent data capture.

## File Location
- Source PDF: `supporting_files/Community Profile of [Community Name].pdf`
- Processed Data: `data/processed/[Community]_demographics.csv`

## Data to Extract

### Basic Information
- [ ] Community Name: _______________________
- [ ] Profile Year/Date: _______________________
- [ ] Geographic Boundaries: _______________________
- [ ] Census Tracts Included: _______________________

### Population Demographics

#### Current Population (Most Recent Year)
- [ ] Total Population: _______________________
- [ ] Black/African American: _______% (________ people)
- [ ] Hispanic/Latino: _______% (________ people)
- [ ] Asian: _______% (________ people)
- [ ] Native American: _______% (________ people)
- [ ] Native Hawaiian/Pacific Islander: _______% (________ people)
- [ ] White (non-Hispanic): _______% (________ people)
- [ ] Other/Multiracial: _______% (________ people)

#### Population Trends (Over Time Period: _______ to _______)
- [ ] Total population change: _______% (increasing/decreasing/stable)
- [ ] Black/African American change: _______% (increasing/decreasing/stable)
- [ ] Hispanic/Latino change: _______% (increasing/decreasing/stable)
- [ ] White (non-Hispanic) change: _______% (increasing/decreasing/stable)
- [ ] Overall demographic shift: [ ] Diversifying [ ] Increasing white [ ] Stable

### Income Data

#### Most Recent Year
- [ ] Median Household Income: $_______________________
- [ ] Mean Household Income: $_______________________
- [ ] Poverty Rate: _______%
- [ ] Families Below Poverty: _______%
- [ ] Per Capita Income: $_______________________

#### Income Trends
- [ ] Median income change: $_______ (% change: _______)
- [ ] Poverty rate change: _______ percentage points
- [ ] Income trend: [ ] Increasing [ ] Decreasing [ ] Stable

### Housing Data

#### Homeownership
- [ ] Overall Homeownership Rate: _______%
- [ ] Homeownership Rate - White: _______%
- [ ] Homeownership Rate - Black: _______%
- [ ] Homeownership Rate - Hispanic: _______%
- [ ] Homeownership Rate - Asian: _______%

#### Housing Values
- [ ] Median Home Value: $_______________________
- [ ] Average Home Value: $_______________________
- [ ] Median Rent: $_______________________/month
- [ ] Average Rent: $_______________________/month

#### Housing Trends
- [ ] Home value change: _______%
- [ ] Rent change: _______%
- [ ] Housing stock change: _______ units

### Historical Context

- [ ] Redlining History: [ ] Yes [ ] No
  - If yes, note: _______________________________________________
- [ ] Disinvestment Patterns: [ ] Yes [ ] No
  - If yes, note: _______________________________________________
- [ ] Recent Development: [ ] Yes [ ] No
  - If yes, note: _______________________________________________

### Additional Context

- [ ] Major Employers: _______________________________________________
- [ ] Educational Attainment (High School+): _______%
- [ ] Educational Attainment (Bachelor's+): _______%
- [ ] Unemployment Rate: _______%
- [ ] Key Industries: _______________________________________________

## How to Use This Template

1. Open the Community Profile PDF
2. Extract data section by section
3. Fill in all relevant fields
4. Save extracted data to CSV in `data/processed/`
5. Reference in member reports using `utils/community_profile.py`

## Example CSV Format

```csv
metric,year,value,unit,notes
total_population,2020,45000,people,
black_percentage,2020,52.3,percent,
hispanic_percentage,2020,28.1,percent,
median_household_income,2020,42800,dollars,
poverty_rate,2020,18.5,percent,
homeownership_rate,2020,45.2,percent,
```

---

*Use this template for each Community Profile to ensure consistent data extraction.*

