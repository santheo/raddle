<script>
  import { onMount } from 'svelte';
  import { load } from 'js-yaml';

  let ladder = $state([]);
  let clues = $state([]);
  let emoji1 = $state([]);
  let emoji2 = $state([]);
  let currentInput = $state('');
  let gameComplete = $state(false);
  let errorMessage = $state('');
  let inputElement; // store the input element reference
  
  onMount(async () => {
    try {
      const response = await fetch('/data/day-night.yaml');
      const text = await response.text();
      const data = load(text);

      emoji1 = data.meta.emoji1;
      emoji2 = data.meta.emoji2;
      
      // Process the ladder data from YAML
      ladder = data.ladder.map((node, index) => {
        let initialStatus = 'unrevealed';
        if (index === 0 || index === data.ladder.length - 2) {
          initialStatus = 'question';
        } else if (index === 1 || index === data.ladder.length - 1) {
          initialStatus = 'answer';
        }

        return {
          word: node.word,
          clue: node.clue,
          transform: index > 0 ? data.ladder[index - 1].transform : "", // Show previous transformation
          isRevealed: index === 0 || index === data.ladder.length - 1,
          isClueShown: false,
          status: initialStatus
        };
      });
      
      // Create alphabetically sorted clues
      clues = data.ladder
        .filter(node => node.clue)
        .map(node => ({
          text: node.clue,
          isUsed: false
        }))
        .sort((a, b) => {
          const cleanA = a.text.replace(/\W/g, '');
          const cleanB = b.text.replace(/\W/g, '');
          return cleanA.localeCompare(cleanB);
        });
      
      // Focus the input element
      inputElement?.focus();
    } catch (error) {
      console.error('Error loading puzzle:', error);
    }
  });

function handleInput(event) {
  if (event.key === 'Enter') {
    const word = currentInput.toUpperCase();
    
    // Find next empty position from top and bottom
    const topIndex = ladder.findIndex(rung => !rung.isRevealed);
    const bottomIndex = ladder.length - 1 - [...ladder].reverse().findIndex(rung => !rung.isRevealed);
    
    // Check if word matches either position
    if (isValidWord(word, topIndex) || isValidWord(word, bottomIndex)) {
      const matchIndex = isValidWord(word, topIndex) ? topIndex : bottomIndex;
      ladder[matchIndex].isRevealed = true;
      updateNextRungs(matchIndex); 
      
      // Show clues based on direction
      if (matchIndex === topIndex) {
        // Going down from top - show clues for all previous rungs
        ladder = ladder.map((rung, i) => ({
          ...rung,
          isClueShown: rung.isClueShown || (i > 0 && i <= matchIndex)
        }));
      } else {
        // Going up from bottom - show clues for all following rungs
        ladder = ladder.map((rung, i) => ({
          ...rung,
          isClueShown: rung.isClueShown || i > matchIndex
        }));
      }

      // Mark clue as used - look at transformation after the word for bottom-up matches
      const clueIndex = clues.findIndex(clue => {
        if (matchIndex === topIndex) {
          // For top-down matches, use previous transformation
          return clue.text === ladder[matchIndex - 1].clue;
        } else {
          // For bottom-up matches, use next transformation
          return clue.text === ladder[matchIndex].clue;
        }
      });
      
      if (clueIndex !== -1) {
        clues[clueIndex].isUsed = true;
      }
      
      currentInput = '';
      errorMessage = '';
      
      // Check if game is complete
      gameComplete = ladder.every(rung => rung.isRevealed);
      
      // If game is complete, mark all clues as used and show all clue transformations
      if (gameComplete) {
        ladder = ladder.map((rung, index) => ({...rung, isClueShown: (index > 0 ? true : false), status: 'revealed'}));
        clues = clues.map(clue => ({...clue, isUsed: true}));
      }
    } else {
      errorMessage = `${word} is not one of the next rungs`;
      currentInput = '';
      inputElement?.focus();
    }
  }
}

  function isValidWord(word, index) {
    return ladder[index]?.word === word;
  }

  function updateNextRungs(revealedIndex) {
    const answerIndexTop = ladder.findIndex(r => r.status == "answer");
    const questionIndexBottom = ladder.length - 1 - [...ladder].reverse().findIndex(r => r.status == "question");
    
    ladder = ladder.map((rung, index) => ({
      ...rung,
      status: determineStatus(rung, index, revealedIndex, answerIndexTop, questionIndexBottom)
    }));
  }

  function determineStatus(rung, index, revealedIndex, answerIndexTop, questionIndexBottom) {
    // If the word was revealed from the top
    if (revealedIndex === answerIndexTop) {
      if (index < revealedIndex) return 'revealed';
      if (index === revealedIndex) return 'question';
      if (index === revealedIndex + 1) return (rung.status === 'question' ? 'both' : 'answer');
    }

    // If the word was revealed from the bottom
    if (revealedIndex === questionIndexBottom) {
      if (index > revealedIndex) return 'revealed';
      if (index === revealedIndex) return 'answer';
      if (index === revealedIndex - 1) return (rung.status === 'answer' ? 'both' : 'question');;
    }
    // For initial state or other cases
    return rung.status;
  }
</script>

<main class="min-h-screen bg-gray-100 p-4">
  <div class="max-w-6xl mx-auto">
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-bold ">RADDLE — The Transformation Ladder Game</h2>
      <p>This is a demo version. It only works on desktop browsers for now. <b>Please don't share.</b> Direct all feedback to <a class="text-blue-600 underline" href="mailto:sandy@mysteryleague.com">sandy@mysteryleague.com</a>.</p>
    </div>  
    <!-- Top section: Input -->
    {#if gameComplete}
      <div class="text-center p-4 bg-green-100 rounded mb-4">
        <h3 class="text-xl font-bold text-green-700">Congratulations!</h3>
        <p>You've successfully climbed the ladder!</p>
      </div>
    {/if}

    <!-- Main grid -->
    <div class="grid grid-cols-1 md:grid-cols-[2fr_3fr] gap-8">

      <!-- Clues -->
      <div class="md:order-2">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="max-w-2xl mx-auto mb-4">
          <input
            bind:this={inputElement}
            type="text"
            bind:value={currentInput}
            onkeydown={handleInput}
            placeholder="Type a word here…"
            class="w-full p-3 border-2 border-blue-300 rounded bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {#if errorMessage}
            <p class="text-red-500 mt-2">{errorMessage}</p>
          {/if}
        </div>

        <p class="mb-4 text-sm">
          Enter the next word in the ladder — by solving one of the clues below.
          It's up to you to determine which one.
          You may enter either the next word going down the ladder, or going up.
        </p>
        <div class="divide-y divide-gray-300">
          {#each clues as clue}
            <div class="pt-2 pb-2 {clue.isUsed ? 'line-through text-gray-400' : ''}">
              {@html clue.text
                .replace('^', `<span class="q-placeholder">&nbsp;</span>`)
                .replace(/\[(.*?)\]/g, `<span class="a-placeholder">$1</span>`)}
            </div>
          {/each}
        </div>

      </div>
      </div>

      <!-- Ladder -->
      <div>
      <div class="bg-white rounded-lg shadow">
        <div class="divide-y divide-gray-300">
          {#each ladder as rung, index}
            <div class="p-3 relative font-mono text-lg {rung.status}" class:bg-yellow-50={rung.status=="answer"} class:bg-green-100={rung.status=="question"}>
              {#if rung.isRevealed}
                {#if rung.isClueShown}
                  <span class="font-sans transform">{rung.transform}</span>
                {/if}
                {rung.word}
              {:else}
                <span class="">
                  {#each rung.word.split(' ') as word, i}
                    <span class="word-box">
                    {#each Array(word.length) as _, j}
                      <span class="letter-box">&nbsp;</span>
                    {/each}
                    </span>
                  {/each}
                  <span class="ml-1">
                    ({rung.word.split(' ').map(w => w.length).join(' ')})
                  </span>
                </span>
              {/if}
            </div>
          {/each}
        </div>
      </div>
        {#if process.env.NODE_ENV === 'development'}
        <div class="mt-4">
          <button
            onclick={() => {
              ladder = ladder.map((rung, index) => ({
                ...rung,
                isRevealed: true,
                isClueShown: index === 0 ? false : true,
                status: 'revealed'
              }));
              
              setTimeout(() => {
                clues = clues.map(clue => ({
                  ...clue,
                  isUsed: true
                }));
                gameComplete = true;
              }, 0);
              gameComplete = true;
            }}
            class="w-full p-2 mt-4 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded"
          >
            [DEBUG] Reveal Ladder
          </button>
        </div>
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }

  :global(.q-placeholder) {
    display: inline-block;
    background-color: rgb(220, 252, 231); /* matches green-100 */
    padding: 0 0.5rem;
    margin-right: 1px;
  }

  :global(.a-placeholder) {
    background-color: oklch(0.987 0.026 102.212); /* matches yellow-50 */
    padding: .2rem .4rem;
  }

  :global(.word-box:not(:first-child)) {
    display: inline-block;
    margin-left: 10px;
  }

  :global(.letter-box) {
    display: inline-block;
    width: 1em;
    height: 1em;
    background: #ccc;
    margin: 0 3px 0 0;
    text-align: center;
    line-height: 1em;
  }
  
  :global(.transform) {
    text-transform: uppercase;
    font-size: .75rem;
    background-color: white;
    border-radius: 6px;
    border: 1px solid #ddd;
    position: absolute;
    top: -.7rem;
    left: calc(var(--spacing)*2);
    padding: .2rem .4rem;
    line-height: 1;
  }
</style>