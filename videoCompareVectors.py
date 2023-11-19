import numpy as np
import json


import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--needle', type=str , required=True)
parser.add_argument('--haystack', type=str , required=True )
parser.add_argument('--threshold', type=float , default=0.95)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def find_longest_consistent_match(needle_frames, haystack_frames, similarity_threshold):
    longest_consistent_match = {
        'needle_start_index': -1,
        'needle_end_index': -1,
        'haystack_start_index': -1,
        'haystack_end_index': -1,
        'match_length': 0,
        'needle_video_length': len(needle_frames),
        'haystack_video_length': len(haystack_frames),
        'average_similarity': 0
    }

    for start_index_needle in range(len(needle_frames)):
        for end_index_needle in range(start_index_needle, len(needle_frames)):
            current_match_length = end_index_needle - start_index_needle + 1

            for start_index_haystack in range(len(haystack_frames) - current_match_length + 1):
                
                frame_similarities = [
                    cosine_similarity(needle_frames[frame_index_needle], haystack_frames[start_index_haystack + (frame_index_needle - start_index_needle)])
                    for frame_index_needle in range(start_index_needle, end_index_needle + 1)
                ]

                if all(similarity >= similarity_threshold for similarity in frame_similarities):
                    if current_match_length > longest_consistent_match['match_length']:
                        longest_consistent_match.update({
                            'needle_video_length': len(needle_frames),
                            'haystack_video_length': len(haystack_frames),
                            'needle_start_index': start_index_needle,
                            'needle_end_index': end_index_needle,
                            'haystack_start_index': start_index_haystack,
                            'haystack_end_index': start_index_haystack + current_match_length - 1,
                            'match_length': current_match_length,
                            'frame_similarities': [float(sim) for sim in frame_similarities],
                            'similarity_threshold': similarity_threshold,
                            'average_similarity': sum(frame_similarities) / len(frame_similarities)
                        })
                        break  # Found the longest consistent match for this start index in the needle

    return longest_consistent_match

def explain_results(match_result):
    if match_result['match_length'] > 0:
        needle_coverage_percent = (match_result['match_length'] / match_result['needle_video_length']) * 100
        haystack_coverage_percent = (match_result['match_length'] / match_result['haystack_video_length']) * 100
        average_similarity_percent = match_result['average_similarity'] * 100

        explanation = (
            f"Match Analysis:\n"
            f" - {needle_coverage_percent:.2f}% of the needle video is potentially included in {haystack_coverage_percent:.2f}% of the haystack video.\n"
            f" - Probability of Match: {average_similarity_percent:.2f}% (based on average similarity).\n"
            f" - Needle Segment: Frames {match_result['needle_start_index']} to {match_result['needle_end_index']}.\n"
            f" - Corresponding Haystack Segment: Frames {match_result['haystack_start_index']} to {match_result['haystack_end_index']}.\n"
            f" - Similarity Threshold for Matching: {match_result['similarity_threshold'] * 100}%."
        )
    else:
        explanation = "No matching segment found that meets the similarity threshold."

    return explanation

if __name__ == "__main__":

    args = parser.parse_args()

    haystack_video = args.haystack
    needle_video = args.needle
    similarity_threshold = args.threshold

    haystack_video_vectors = np.load(haystack_video + '.npy')
    needle_video_vectors = np.load(needle_video + '.npy')


    result = find_longest_consistent_match(needle_video_vectors, haystack_video_vectors, similarity_threshold)
    print(json.dumps(result, indent=4 , sort_keys=False))
    #print(explain_results(result))
    #[ print(f"{n}") for n in result.get('frame_similarities',[]) ]